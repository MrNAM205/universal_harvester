# universal_harvester/agent/copilot_scraper.py
"""
Copilot sidebar + chat harvester module.
"""
from __future__ import annotations

import os
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

# ============================================================
#  COPILOT SIDEBAR CONTROL MODULE (FULLY REWRITTEN)
# ============================================================

# =========================
# Data models
# =========================
@dataclass
class ChatMeta:
    index: int
    title: str
    aria_label: str


@dataclass
class ChatData:
    meta: ChatMeta
    messages: List[Dict[str, Any]]


# =========================
# Sidebar & Logging
# =========================
def _log(msg: str) -> None:
    print(f"[COPILOT] {msg}")


def ensure_sidebar_open(page: Page) -> None:
    """
    Ensures the Copilot sidebar is open.
    """
    _log("Ensuring sidebar is open...")
    toggle = page.locator('button[data-testid="sidebar-toggle-button"]')
    if toggle.count() > 0:
        try:
            # Check if sidebar is already open
            if toggle.first.get_attribute("aria-expanded") == "true":
                return
            toggle.first.click()
            page.wait_for_timeout(300)
        except Exception:
            pass


def enumerate_chats(page: Page, timeout: int = 15000) -> List[ChatMeta]:
    """
    Enumerate all chats in the sidebar by handling virtual scrolling. This function is fully stable and React-safe.
    """
    _log("Enumerating all chats in sidebar (Chrome‑safe virtual scroll)...")
    ensure_sidebar_open(page)

    item_selector = 'div[role="link"]:has(button[id^="conversation-options-"])'
    try:
        page.wait_for_selector(item_selector, timeout=timeout)
    except PlaywrightTimeoutError:
        raise RuntimeError("Chat items not visible; sidebar structure may have changed.")

    # --- Chrome Virtual Scroll Stabilizer ---
    last_count = -1
    while True:
        items = page.locator(item_selector)
        current_count = items.count()

        if current_count == last_count:
            break

        last_count = current_count

        if current_count > 0:
            try:
                items.nth(current_count - 1).scroll_into_view_if_needed()
            except Exception:
                pass

        page.wait_for_timeout(800)

    items_locator = page.locator(item_selector)
    items = items_locator.all()
    _log(f"Final count: Found {len(items)} total chats.")
    
    all_meta: List[ChatMeta] = []
    for i, item in enumerate(items):
        aria_label = item.get_attribute("aria-label") or f"Chat {i}"
        
        title_el = item.locator("p.truncate, p[title]")
        if title_el.count() > 0:
            title = title_el.first.get_attribute("title") or title_el.first.inner_text().strip()
        else:
            title = item.inner_text().strip()
            
        all_meta.append(ChatMeta(index=i, title=title, aria_label=aria_label))

    return all_meta


# =========================
# Chat Harvesting Helpers
# =========================
def _open_chat_from_sidebar(page: Page, meta: ChatMeta, timeout: int = 15000) -> None:
    _log(f"Opening chat from sidebar: index={meta.index}, title={meta.title!r}")
    ensure_sidebar_open(page)

    item_selector = 'div[role="link"]:has(button[id^="conversation-options-"])'
    page.wait_for_selector(item_selector, timeout=timeout)

    chat_items = page.locator(item_selector)

    if meta.index >= chat_items.count():
        raise RuntimeError(
            f"Chat index {meta.index} out of range; only {chat_items.count()} items visible."
        )

    chat_items.nth(meta.index).click()
    page.wait_for_timeout(1500)


def extract_messages_cdp(page: Page) -> List[Dict[str, Any]]:
    """
    Extracts messages using Chrome DevTools Protocol (CDP)
    via DOMSnapshot.captureSnapshot.
    """
    client = page.context.new_cdp_session(page)

    snapshot = client.send("DOMSnapshot.captureSnapshot", {
        "computedStyles": [],
        "includeDOMRects": False,
        "includePaintOrder": False
    })

    strings = snapshot["strings"]
    nodes = snapshot["documents"][0]["nodes"]

    # Extract text nodes
    text_content = nodes["text"]
    node_names = nodes["nodeName"]

    messages = []
    current_role = None
    current_text = []

    for i, name_idx in enumerate(node_names):
        name = strings[name_idx]

        # Detect message author
        if name.lower() == "div":
            attrs = nodes.get("attributes", [])
            if i < len(attrs) and attrs[i]:
                attr_strings = [strings[a] for a in attrs[i]]
                if "data-message-author" in attr_strings:
                    idx = attr_strings.index("data-message-author") + 1
                    current_role = attr_strings[idx]

        # Detect text content
        if i < len(text_content) and text_content[i] != -1:
            text = strings[text_content[i]].strip()
            if text:
                current_text.append(text)

        # When role changes or block ends, flush
        if current_role and current_text:
            messages.append({
                "role": "user" if "user" in current_role.lower() else "assistant",
                "text": "\n".join(current_text)
            })
            current_text = []
            current_role = None

    return messages

def hydrate_messages(page: Page) -> int:
    """
    Scrolls the conversation container upward until all messages are hydrated.
    Copilot uses virtualization, so older messages only load when scrolled.
    """

    # Identify the correct scroll container safely without strict mode violations
    candidates = [
        '[data-message-container]',
        'div[data-testid="backstage-chats"]',
        'div[data-testid="chat-page"] div[class*="overflow-y-auto"]',
        'div[data-testid="chat-page"]'
    ]

    scroll_container = None
    for sel in candidates:
        loc = page.locator(sel)
        if loc.count() > 0:
            scroll_container = loc.first
            break

    if scroll_container is None:
        _log("ERROR: No valid scroll container found.")
        return 0

    last_count = -1

    for _ in range(80):  # increased cap for long chats
        messages = page.locator(
            'div[class*="group/user-message"], div[class*="group/ai-message"], div[data-message-author]'
        )
        count = messages.count()

        if count == last_count:
            break

        last_count = count

        # Scroll upward to load older messages
        try:
            scroll_container.evaluate("el => { el.scrollTop = 0; }")
        except Exception:
            pass
        page.wait_for_timeout(500)

    return last_count


def extract_ai_text(block) -> str:
    """
    Extracts ALL text from an AI message block, including:
    - multi-part messages
    - nested spans
    - markdown-rendered HTML
    - code blocks
    - multi-node content segments
    """
    segments = block.locator('[id*="content"]').all()
    collected = []

    for seg in segments:
        txt = seg.inner_text().strip()
        if txt:
            collected.append(txt)

    # Fallback for older Copilot layouts
    if not collected:
        fallback = block.locator('div[data-content="ai-message"]')
        if fallback.count():
            txt = fallback.inner_text().strip()
            if txt:
                collected.append(txt)

    return "\n\n".join(collected)


def _extract_chat_messages(page: Page) -> List[Dict[str, Any]]:
    """
    Extracts ALL user + AI messages from the hydrated conversation.
    Ensures correct chronological order.
    """
    _log("Extracting messages from current chat...")

    messages = []
    
    # Locate all message blocks in visual DOM order
    message_selector = 'div[data-message-author], div[class*="group/user-message"], div[class*="group/ai-message"]'
    blocks = page.locator(message_selector).all()
    
    for i, block in enumerate(blocks):
        role = block.get_attribute("data-message-author")
        if not role:
            # Fallback based on class/outerHTML
            html = block.evaluate("el => el.outerHTML")
            if "user-message" in html:
                role = "user"
            elif "ai-message" in html:
                role = "assistant"
            else:
                continue

        role = "user" if "user" in role.lower() else "assistant"
        msg_id = block.get_attribute("id") or f"{role}-{i}"

        if role == "user":
            text_el = block.locator('div[data-content="user-message"]')
            if text_el.count() > 0:
                text = text_el.first.inner_text().strip()
            else:
                text = block.inner_text().strip()
        else:
            text = extract_ai_text(block)
            if not text.strip():
                text = block.inner_text().strip()

        messages.append({
            "id": msg_id,
            "role": role,
            "text": text
        })

    _log(f"Extracted {len(messages)} messages.")
    return messages


def harvest_chat(page: Page, meta: ChatMeta) -> ChatData:
    """
    Clicks into a chat, scrolls to hydrate messages, and extracts the bubbles.
    """
    _open_chat_from_sidebar(page, meta)
    
    # Force scroll-up hydration before any extraction attempts
    hydrate_messages(page)
    
    try:
        messages = extract_messages_cdp(page)
        if not messages:
            messages = _extract_chat_messages(page)
    except Exception:
        messages = _extract_chat_messages(page)
        
    return ChatData(meta=meta, messages=messages)


# =========================
# Main entry: harvest_all_chats
# =========================
def harvest_all_chats(page: Page, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point: Normalizes state, enumerates all chats, and harvests them.
    Includes Resume-On-Crash via harvest_state.json.
    """
    if url:
        _log(f"Harvesting from Copilot URL: {url}")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
    except PlaywrightTimeoutError:
        _log("domcontentloaded timeout – continuing anyway")

    ensure_sidebar_open(page)
    all_meta = enumerate_chats(page)

    results: List[Dict[str, Any]] = []

    # =========================
    # Resume-On-Crash State Loader
    # =========================
    export_dir = os.path.join(os.getcwd(), "exports")
    os.makedirs(export_dir, exist_ok=True)
    state_file = os.path.join(export_dir, "harvest_state.json")
    completed_indices = set()
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                completed_indices = set(json.load(f))
            _log(f"Resuming from state file. {len(completed_indices)} chats already harvested.")
        except Exception as e:
            _log(f"Warning: Could not read state file ({e}). Starting fresh.")

    for meta in all_meta:
        if meta.index in completed_indices:
            _log(f"Skipping already harvested chat: {meta.title} (Index {meta.index})")
            continue

        try:
            chat_data = harvest_chat(page, meta)

            # Get actual chat ID from URL
            chat_id = page.url.rstrip("/").split("/")[-1]

            chat_dict = {
                "index": meta.index,
                "title": meta.title,
                "chat_id": chat_id,
                "aria_label": meta.aria_label,
                "messages": chat_data.messages,
            }
            results.append(chat_dict)

            # Save progress after every successful chat
            completed_indices.add(meta.index)
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(list(completed_indices), f)
                
            # Stream export to Markdown immediately
            from universal_harvester.utils.exporter import export_to_markdown
            export_to_markdown({"chats": [chat_dict]}, output_dir=export_dir)
            
        except Exception as e:
            _log(f"Failed to harvest chat index {meta.index} ({meta.title}): {e}")
            _log("Continuing to next chat...")

    return {
        "source": "copilot.microsoft.com",
        "url": url,
        "harvested_at": datetime.now(timezone.utc).isoformat(),
        "page_type": "copilot_multi_chat",
        "analysis": {
            "total_chats_found": len(all_meta),
            "total_chats_harvested": len(results),
        },
        "chats": results,
    }
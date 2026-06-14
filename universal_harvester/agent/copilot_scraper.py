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
from datetime import datetime

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


REAL_TOGGLE = 'button[data-testid="sidebar-toggle-button"]:visible, button[id="sidebar-toggle-button"]:visible, button[aria-controls="sidebar-container"]:visible'


def sidebar_is_open(page: Page) -> bool:
    """Return True if the sidebar is currently open."""
    try:
        toggle = page.locator(REAL_TOGGLE)
        if toggle.count() == 0:
            return False
        expanded = toggle.get_attribute("aria-expanded")
        return expanded == "true"
    except Exception:
        return False


def sidebar_is_visible(page: Page) -> bool:
    """Return True if the sidebar container is visible."""
    return page.locator('div[id="sidebar-container"]:visible, div[role="listbox"]:visible, div[data-testid="sidebar-expanded-content"]:visible').count() > 0


def reveal_toggle_button(page: Page) -> None:
    """
    Copilot hides the toggle in mobile/narrow mode.
    Hovering the left edge reveals it.
    """
    page.mouse.move(5, 200)
    page.wait_for_timeout(250)


def click_real_toggle(page: Page) -> bool:
    """
    Click ONLY the visible toggle button.
    Avoids the invisible overlay button.
    """
    toggle = page.locator(REAL_TOGGLE)

    if toggle.count() == 0:
        reveal_toggle_button(page)
        toggle = page.locator(REAL_TOGGLE)

    if toggle.count() == 0:
        return False

    if toggle.is_visible():
        toggle.click()
        page.wait_for_timeout(400)
        return True

    return False


def force_open_sidebar(page: Page) -> None:
    """
    Last-resort fallback: force the sidebar to display via CSS.
    Safe because it only affects visibility, not layout logic.
    """
    page.evaluate(
        """
        () => {
            const el = document.querySelector('#sidebar-container');
            if (el) el.style.display = 'block';
        }
        """
    )
    page.wait_for_timeout(300)


def ensure_sidebar_open(page: Page) -> None:
    """
    Master function:
    - Detects current state
    - Reveals toggle if hidden
    - Clicks only the real toggle
    - Falls back to keyboard shortcut
    - Falls back to CSS injection
    """
    _log("Ensuring sidebar is open...")

    if sidebar_is_open(page) and sidebar_is_visible(page):
        return

    if click_real_toggle(page):
        if sidebar_is_visible(page):
            return

    # Keyboard shortcut fallback
    page.keyboard.down("Control")
    page.keyboard.down("Shift")
    page.keyboard.press("y")
    page.keyboard.up("Shift")
    page.keyboard.up("Control")
    page.wait_for_timeout(500)

    if sidebar_is_visible(page):
        return

    # CSS fallback
    force_open_sidebar(page)


def enumerate_chats(page: Page, timeout: int = 15000) -> List[ChatMeta]:
    """
    Enumerate all chats in the sidebar by handling virtual scrolling.
    This function is fully stable and React-safe.
    """
    _log("Enumerating all chats in sidebar (Chrome‑safe virtual scroll)...")
    ensure_sidebar_open(page)

    listbox_selector = '[data-testid="chat-history-list"], div[role="listbox"]'
    try:
        page.wait_for_selector(listbox_selector, timeout=timeout)
    except PlaywrightTimeoutError:
        raise RuntimeError("Chat listbox not visible; sidebar structure may have changed.")

    sidebar = page.locator(listbox_selector).first

    # --- Chrome Virtual Scroll Stabilizer ---
    last_count = -1
    while True:
        items = sidebar.locator(
            '[data-testid="chat-history-item"], div[role="option"], a[href*="/chats/"]'
        )
        current_count = items.count()

        if current_count == last_count:
            break

        last_count = current_count

        # Scroll last item into view
        items.nth(current_count - 1).scroll_into_view_if_needed()

        # Chrome-safe absolute scroll
        sidebar.evaluate("el => { el.scrollTop = el.scrollHeight; }")

        page.wait_for_timeout(800)

    items_locator = sidebar.locator(
        '[data-testid="chat-history-item"], div[role="option"], a[href*="/chats/"]'
    )
    items = items_locator.all()
    _log(f"Final count: Found {len(items)} total chats.")

    all_meta: List[ChatMeta] = []
    for i, item in enumerate(items):
        aria_label = item.get_attribute("aria-label") or f"Chat {i}"
        
        title_el = item.locator("p[title]")
        if title_el.count() > 0:
            title = title_el.first.get_attribute("title")
        else:
            title = item.inner_text().strip()
            
        title = title or aria_label

        all_meta.append(ChatMeta(index=i, title=title, aria_label=aria_label))

    return all_meta


# =========================
# Chat Harvesting Helpers
# =========================
def _open_chat_from_sidebar(page: Page, meta: ChatMeta, timeout: int = 15000) -> None:
    _log(f"Opening chat from sidebar: index={meta.index}, title={meta.title!r}")
    ensure_sidebar_open(page)

    sidebar = page.locator('[data-testid="chat-history-list"], div[role="listbox"]').first
    sidebar.wait_for(state="visible", timeout=timeout)

    chat_items = sidebar.locator(
        '[data-testid="chat-history-item"], div[role="option"], a[href*="/chats/"]'
    )

    if meta.index >= chat_items.count():
        raise IndexError(f"Chat index {meta.index} out of range.")

    item = chat_items.nth(meta.index)

    # Ensure Chrome loads the element
    item.scroll_into_view_if_needed()
    item.evaluate("el => el.scrollIntoView(true);")
    item.click()

    page.wait_for_timeout(1500)

    # --- Chrome-safe scroll container detection ---
    candidates = [
        '[data-message-container]',
        'div[data-testid="backstage-chats"]',
        'div[data-testid="chat-page"] div[class*="overflow-y-auto"]',
        'div[data-testid="chat-page"]'
    ]

    scroll_container = None
    for sel in candidates:
        try:
            scroll_container = page.locator(sel).first
            scroll_container.wait_for(state="visible", timeout=2000)
            break
        except Exception:
            continue

    if scroll_container is None:
        raise RuntimeError("Could not locate chat scroll container.")

    # --- Chrome-safe scroll-to-top (lazy-load older messages) ---
    last_height = None
    while True:
        scroll_container.evaluate("el => { el.scrollTop = 0; }")
        page.wait_for_timeout(800)

        new_height = scroll_container.evaluate("el => el.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

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
            'div[class*="group/user-message"], div[class*="group/ai-message"]'
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

    # Ensure all messages are loaded
    hydrate_messages(page)

    messages = []

    # USER MESSAGES
    for i, block in enumerate(page.locator('div[class*="group/user-message"]').all()):
        text_el = block.locator('div[data-content="user-message"]')
        text = text_el.inner_text().strip() if text_el.count() else ""
        msg_id = block.get_attribute("id") or f"user-{i}"

        messages.append({
            "id": msg_id,
            "role": "user",
            "text": text
        })

    # AI MESSAGES
    for i, block in enumerate(page.locator('div[class*="group/ai-message"]').all()):
        msg_id = block.get_attribute("id") or f"assistant-{i}"
        text = extract_ai_text(block)

        if text.strip():
            messages.append({
                "id": msg_id,
                "role": "assistant",
                "text": text
            })

    # Sort chronologically by message ID
    messages.sort(key=lambda m: m.get("id", ""))

    _log(f"Extracted {len(messages)} messages.")
    return messages


def harvest_chat(page: Page, meta: ChatMeta) -> ChatData:
    """
    Clicks into a chat, scrolls to hydrate messages, and extracts the bubbles.
    """
    _open_chat_from_sidebar(page, meta)
    
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
    state_file = "harvest_state.json"
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
            export_to_markdown({"chats": [chat_dict]}, output_dir=os.path.join(os.getcwd(), "exports"))
            
        except Exception as e:
            _log(f"Failed to harvest chat index {meta.index} ({meta.title}): {e}")
            _log("Continuing to next chat...")

    return {
        "source": "copilot.microsoft.com",
        "url": url,
        "harvested_at": datetime.utcnow().isoformat() + "Z",
        "page_type": "copilot_multi_chat",
        "analysis": {
            "total_chats_found": len(all_meta),
            "total_chats_harvested": len(results),
        },
        "chats": results,
    }
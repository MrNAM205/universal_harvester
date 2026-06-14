# universal_harvester/agent/detector.py
from dataclasses import dataclass
from typing import Literal, Dict, Any
from playwright.sync_api import Page


PageType = Literal["static", "dynamic", "shadow", "infinite_scroll"]


@dataclass
class PageAnalysis:
    page_type: PageType
    shadow_roots: bool
    dynamic_scripts: bool
    infinite_scroll: bool
    raw_signals: Dict[str, Any]


def detect_page_type(page: Page) -> PageAnalysis:
    signals = page.evaluate(
        """
        () => {
            const scripts = document.querySelectorAll('script').length;
            const customElements = Array.from(document.querySelectorAll('*'))
                .filter(el => el.tagName.includes('-')).length;

            const hasShadow = (() => {
                const walker = document.createTreeWalker(
                    document,
                    NodeFilter.SHOW_ELEMENT,
                    null
                );
                let node;
                while (node = walker.nextNode()) {
                    if (node.shadowRoot) return true;
                }
                return false;
            })();

            const bodyTextLen = document.body.innerText.length;

            return {
                scripts,
                customElements,
                hasShadow,
                bodyTextLen
            };
        }
        """
    )

    scripts = signals["scripts"]
    custom = signals["customElements"]
    has_shadow = signals["hasShadow"]
    body_len = signals["bodyTextLen"]

    # Very simple heuristic to start; you can tune later
    dynamic = scripts > 5 or custom > 5
    infinite_scroll = False  # upgraded later if needed

    if has_shadow:
        page_type: PageType = "shadow"
    elif dynamic:
        page_type = "dynamic"
    else:
        page_type = "static"

    return PageAnalysis(
        page_type=page_type,
        shadow_roots=has_shadow,
        dynamic_scripts=dynamic,
        infinite_scroll=infinite_scroll,
        raw_signals=signals,
    )

# universal_harvester/agent/scraper.py
from typing import Dict, Any, List
from playwright.sync_api import Page
from bs4 import BeautifulSoup

from universal_harvester.utils.text_cleaner import clean_html_to_text
from universal_harvester.agent.detector import PageAnalysis


def _extract_links(page: Page) -> List[Dict[str, str]]:
    return page.evaluate(
        """
        () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
            href: a.href,
            text: a.innerText.trim()
        }))
        """
    )


def scrape_static(page: Page) -> Dict[str, Any]:
    html = page.content()
    text = clean_html_to_text(html)
    links = _extract_links(page)
    title = page.title()
    return {"title": title, "text": text, "links": links}


def scrape_dynamic(page: Page) -> Dict[str, Any]:
    # For now, same as static but after JS has run
    html = page.content()
    text = clean_html_to_text(html)
    links = _extract_links(page)
    title = page.title()
    return {"title": title, "text": text, "links": links}


def scrape_shadow(page: Page) -> Dict[str, Any]:
    # Deep text extraction through shadow roots
    text = page.evaluate(
        """
        () => {
            function deepText(node) {
                let out = "";
                if (node.nodeType === Node.TEXT_NODE) {
                    const t = node.textContent.trim();
                    if (t) out += t + " ";
                }
                if (node.shadowRoot) {
                    out += deepText(node.shadowRoot);
                }
                for (const child of node.childNodes) {
                    out += deepText(child);
                }
                return out;
            }
            return deepText(document.body);
        }
        """
    )
    links = _extract_links(page)
    title = page.title()
    return {"title": title, "text": text, "links": links}


def scrape_infinite_scroll(page: Page, max_rounds: int = 10) -> Dict[str, Any]:
    last_height = 0
    for _ in range(max_rounds):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = page.content()
    text = clean_html_to_text(html)
    links = _extract_links(page)
    title = page.title()
    return {"title": title, "text": text, "links": links}


def adaptive_scrape(page: Page, analysis: PageAnalysis) -> Dict[str, Any]:
    if analysis.page_type == "shadow":
        result = scrape_shadow(page)
    elif analysis.page_type == "dynamic":
        result = scrape_dynamic(page)
    elif analysis.page_type == "static":
        result = scrape_static(page)
    else:
        result = scrape_infinite_scroll(page)

    result["page_type"] = analysis.page_type
    result["analysis"] = {
        "shadow_roots": analysis.shadow_roots,
        "dynamic_scripts": analysis.dynamic_scripts,
        "infinite_scroll": analysis.infinite_scroll,
        "raw_signals": analysis.raw_signals,
    }
    return result

# universal_harvester/utils/html_tools.py

from bs4 import BeautifulSoup

def extract_visible_text(html: str) -> str:
    """
    Extracts visible text from HTML while ignoring scripts, styles,
    and hidden elements. This is a fallback helper used by the scraper.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, and noscript
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Remove hidden elements
    for tag in soup.find_all(style=True):
        style = tag["style"].lower()
        if "display:none" in style or "visibility:hidden" in style:
            tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def normalize_html(html: str) -> str:
    """
    Normalizes HTML by pretty-printing and removing noise.
    Useful for debugging or storing snapshots.
    """
    soup = BeautifulSoup(html, "lxml")
    return soup.prettify()

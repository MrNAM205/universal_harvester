# universal_harvester/utils/text_cleaner.py
from bs4 import BeautifulSoup


def clean_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Remove obvious layout noise (very naive starter)
    for tag in soup.find_all(True):
        classes = " ".join(tag.get("class", []))
        if any(k in classes for k in ["flex", "grid", "container", "sidebar", "nav"]):
            # don't always remove, but this is a starting heuristic
            continue

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)

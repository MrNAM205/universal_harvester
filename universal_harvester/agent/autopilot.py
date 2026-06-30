from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse

from universal_harvester.agent.harvester import UniversalHarvester


class HarvesterAutopilot:
    def __init__(self, headed: bool = True, max_depth: int = 2, same_domain_only: bool = True):
        self.headed = headed
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.harvester = UniversalHarvester(headed=headed)

    def _filter_links(self, base_url: str, links: List[Dict[str, str]]) -> List[str]:
        base_domain = urlparse(base_url).netloc
        out = []
        for link in links:
            href = link.get("href")
            if not href:
                continue
            full = urljoin(base_url, href)
            if self.same_domain_only:
                if urlparse(full).netloc != base_domain:
                    continue
            out.append(full)
        return list(set(out))

    def crawl(self, seed_urls: List[str]) -> List[Dict[str, Any]]:
        visited: Set[str] = set()
        queue: List[Dict[str, Any]] = []

        for url in seed_urls:
            queue.append({"url": url, "depth": 0})

        results: List[Dict[str, Any]] = []

        while queue:
            item = queue.pop(0)
            url = item["url"]
            depth = item["depth"]

            if url in visited:
                continue
            visited.add(url)

            print(f"\n[AUTOPILOT] Harvesting {url} at depth {depth}")

            result = self.harvester.harvest(url)
            result["depth"] = depth
            results.append(result)

            if depth < self.max_depth:
                links = result.get("links", [])
                next_urls = self._filter_links(url, links)
                for nxt in next_urls:
                    if nxt not in visited:
                        queue.append({"url": nxt, "depth": depth + 1})

        return results

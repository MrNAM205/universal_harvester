# universal_harvester/agent/completeness_verification.py

from typing import List, Dict, Any


class CompletenessReport:
    def __init__(
        self,
        api_chat_ids: List[str],
        harvested_chat_ids: List[str],
        sidebar_titles: List[str],
        endpoint_profile: Dict[str, Any],
    ):
        self.api_chat_ids = api_chat_ids
        self.harvested_chat_ids = harvested_chat_ids
        self.sidebar_titles = sidebar_titles
        self.endpoint_profile = endpoint_profile

        self.missing_from_harvest = sorted(set(api_chat_ids) - set(harvested_chat_ids))
        self.extra_in_harvest = sorted(set(harvested_chat_ids) - set(api_chat_ids))

    def is_complete(self) -> bool:
        return not self.missing_from_harvest and not self.extra_in_harvest

    def summary(self) -> str:
        lines = []
        lines.append("=== COMPLETENESS VERIFICATION REPORT ===")
        lines.append(f"\nAPI chat count:       {len(self.api_chat_ids)}")
        lines.append(f"Harvested chat count: {len(self.harvested_chat_ids)}")
        lines.append(f"Sidebar visible:      {len(self.sidebar_titles)}")

        if self.is_complete():
            lines.append("\n✔ Harvest is COMPLETE — all chats accounted for.")
        else:
            lines.append("\n✖ Harvest is INCOMPLETE — discrepancies detected.")

        if self.missing_from_harvest:
            lines.append("\nMissing from harvest:")
            for cid in self.missing_from_harvest:
                lines.append(f"  - {cid}")

        if self.extra_in_harvest:
            lines.append("\nExtra in harvest (not in API):")
            for cid in self.extra_in_harvest:
                lines.append(f"  - {cid}")

        if self.endpoint_profile.get("archive_endpoints"):
            lines.append("\n⚠ Archive endpoints detected — ensure they are harvested.")

        if self.endpoint_profile.get("unknown_conversation_like"):
            lines.append(
                "\n⚠ Unknown conversation-like endpoints detected — Copilot may have introduced new APIs."
            )

        return "\n".join(lines)


class CompletenessVerifier:
    @staticmethod
    def verify(
        api_chat_ids: List[str], harvested_chat_ids: List[str], sidebar_titles: List[str], endpoint_profile: Dict[str, Any]
    ) -> CompletenessReport:
        return CompletenessReport(api_chat_ids, harvested_chat_ids, sidebar_titles, endpoint_profile)
import os
import sys
from universal_harvester.diagnostics.network_diag import NetworkDiagnostics


class PreflightFailure(Exception):
    pass


class HarvesterPreflight:
    def __init__(self, strict=True):
        self.strict = strict
        self.diag = NetworkDiagnostics()

    def run(self):
        results = self.diag.run_all()

        failures = [msg for status, msg in results if status == "FAIL"]

        # Check critical items
        critical = [
            "DNS resolution failed",
            "HTTPS connection failed",
            "HF_API_KEY not set",
            "HF_API_KEY invalid",
            "Node.js not found",
            "Unsupported Node.js version",
            "Playwright browser launch failed",
        ]

        critical_hits = [
            f for f in failures
            if any(c in f for c in critical)
        ]

        if critical_hits:
            print("\n[PREFLIGHT] ❌ Environment not healthy:")
            for f in critical_hits:
                print(f"  - {f}")

            if self.strict:
                raise PreflightFailure(
                    "Harvester preflight failed. Fix environment before running pipeline."
                )
            else:
                print("[PREFLIGHT] ⚠ Continuing despite failures (strict=False).")
        else:
            print("\n[PREFLIGHT] ✅ Environment healthy. Harvester may launch.")


def run_preflight(strict=True):
    pf = HarvesterPreflight(strict=strict)
    pf.run()

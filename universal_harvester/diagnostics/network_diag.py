import socket
import ssl
import requests
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class NetworkDiagnostics:
    def __init__(self):
        self.results = []

    def log(self, status, message):
        self.results.append((status, message))
        print(f"[{status}] {message}")

    def test_dns(self, host="api-inference.huggingface.co"):
        try:
            socket.gethostbyname(host)
            self.log("OK", f"DNS resolved: {host}")
        except Exception as e:
            self.log("FAIL", f"DNS resolution failed for {host}: {e}")

    def test_https(self, host="https://api-inference.huggingface.co"):
        try:
            r = requests.get(host, timeout=5)
            self.log("OK", f"HTTPS reachable: {host} (status {r.status_code})")
        except Exception as e:
            self.log("FAIL", f"HTTPS connection failed: {e}")

    def test_hf_api_key(self):
        key = os.getenv("HF_API_KEY")
        if not key:
            self.log("FAIL", "HF_API_KEY not set in environment.")
            return

        try:
            r = requests.get(
                "https://api-inference.huggingface.co/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=5
            )
            if r.status_code == 200:
                self.log("OK", "HF_API_KEY is valid.")
            else:
                self.log("FAIL", f"HF_API_KEY invalid or unauthorized (status {r.status_code}).")
        except Exception as e:
            self.log("FAIL", f"HF_API_KEY test failed: {e}")

    def test_node_version(self):
        try:
            out = subprocess.check_output(["node", "-v"], text=True).strip()
            if out.startswith("v20") or out.startswith("v18"):
                self.log("OK", f"Node.js version supported: {out}")
            else:
                self.log("FAIL", f"Unsupported Node.js version for Playwright: {out}")
        except Exception as e:
            self.log("FAIL", f"Node.js not found or error: {e}")

    def test_playwright(self):
        try:
            subprocess.check_output(
                [sys.executable, "-c",
                 "from playwright.sync_api import sync_playwright; "
                 "with sync_playwright() as p: "
                 " b=p.chromium.launch(headless=True); "
                 " p=b.new_page(); "
                 " p.goto('https://example.com'); "
                 " b.close()"],
                stderr=subprocess.STDOUT
            )
            self.log("OK", "Playwright browser launch successful.")
        except Exception as e:
            self.log("FAIL", f"Playwright browser launch failed: {e}")

    def test_clock_skew(self):
        try:
            local = datetime.utcnow()
            r = requests.get("https://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5)
            remote = datetime.fromisoformat(r.json()["utc_datetime"].replace("Z", "+00:00"))
            skew = abs((remote - local).total_seconds())

            if skew < 10:
                self.log("OK", f"System clock accurate (skew {skew:.2f}s).")
            else:
                self.log("FAIL", f"Clock skew too high ({skew:.2f}s). HTTPS may break.")
        except Exception as e:
            self.log("FAIL", f"Clock skew test failed: {e}")

    def run_all(self):
        print("\n========================================")
        print(" UNIVERSAL HARVESTER - NETWORK DIAGNOSTICS")
        print("========================================\n")

        self.test_dns()
        self.test_https()
        self.test_hf_api_key()
        self.test_node_version()
        self.test_playwright()
        self.test_clock_skew()

        print("\n========================================")
        print(" DIAGNOSTICS COMPLETE")
        print("========================================\n")

        return self.results

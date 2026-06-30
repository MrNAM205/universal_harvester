# scripts/test_brain.py
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from dotenv import load_dotenv
load_dotenv()

from universal_harvester.agent.brain import BrixBrain

def main():
    print("=== OMNIVERO BRIX Brain Verification ===")
    
    brain = BrixBrain()
    status = brain.get_status()
    
    print("\n[STATUS]")
    for k, v in status.items():
        print(f"  {k}: {v}")
        
    print("\n[TEST CHAT] Sending message: 'Hello, who are you?'")
    response = brain.chat("Hello, who are you?")
    
    print("\n[THOUGHT LEDGER]")
    print(response.get("thought_ledger"))
    
    print("\n[RESPONSE]")
    print(response.get("response"))
    
    # Simple assertion
    assert "thought_ledger" in response, "Missing thought_ledger"
    assert "response" in response, "Missing response"
    print("\n[PASS] Verification successful.")

if __name__ == "__main__":
    main()

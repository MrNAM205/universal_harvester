# scripts/test_memory.py
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from dotenv import load_dotenv
load_dotenv()

from universal_harvester.agent.brain import BrixBrain

def main():
    print("=== OMNIVERO BRIX Memory & Ingestion Verification ===")
    
    brain = BrixBrain()
    
    # Test 1: Listing chats
    print("\n[TEST 1] Asking: 'What chats do you have in your database?'")
    history_1 = []
    response_1 = brain.chat("What chats do you have in your database?", history_1)
    
    print("\n[THOUGHT LEDGER]")
    print(response_1.get("thought_ledger"))
    
    print("\n[FINAL RESPONSE]")
    print(response_1.get("response"))
    
    print("\n[CONVERSATION HISTORY SIZE]:", len(history_1))
    for i, h in enumerate(history_1):
        print(f"  Turn {i+1} [{h['role'].upper()}]: {h['content'][:100]}...")

    # Test 2: Keyword Search
    print("\n" + "="*40)
    print("[TEST 2] Asking: 'Search my chats for anything related to cookies or auth.'")
    history_2 = []
    response_2 = brain.chat("Search my chats for anything related to cookies or auth.", history_2)
    
    print("\n[THOUGHT LEDGER]")
    print(response_2.get("thought_ledger"))
    
    print("\n[FINAL RESPONSE]")
    print(response_2.get("response"))

if __name__ == "__main__":
    main()

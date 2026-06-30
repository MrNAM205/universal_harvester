import pytest
from universal_harvester.agent.merge_engine import merge_messages

def test_merge_messages_empty():
    assert merge_messages([], []) == []

def test_merge_messages_basic():
    api_msgs = [
        {"id": "1", "content": [{"type": "text", "text": "Hello"}], "author": {"type": "user"}},
        {"id": "2", "content": [{"type": "text", "text": "Hi"}], "author": {"type": "bot"}}
    ]
    
    ui_msgs = [
        {"id": "1", "content": [{"type": "text", "text": "Hello"}], "author": {"type": "user"}},
        {"id": "2", "content": [{"type": "text", "text": "Hi UI"}], "author": {"type": "bot"}}
    ]
    
    merged = merge_messages(api_msgs, ui_msgs)
    assert len(merged) == 2
    # API takes precedence usually, though merge engine logic dictates specific behavior.
    assert merged[0]["id"] == "1"
    assert merged[1]["id"] == "2"

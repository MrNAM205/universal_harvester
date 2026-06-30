import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from universal_harvester.hud.telemetry_bus import TelemetryBus
from universal_harvester.agent.brain import BrixBrain
from universal_harvester.registry import list_all_chats, get_chat_messages

app = FastAPI()
_bus = TelemetryBus()
brain = BrixBrain()

# Simple in-memory session history
sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

def get_bus() -> TelemetryBus:
    return _bus

@app.get("/")
async def index():
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/stream")
async def stream():
    return StreamingResponse(_bus.stream(), media_type="text/event-stream")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    history = sessions.setdefault(req.session_id, [])
    
    # Send message to brain
    response_dict = brain.chat(req.message, history)
    
    # Record conversation history
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": response_dict["response"]})
    
    # Cap history at last 20 messages
    if len(history) > 20:
        sessions[req.session_id] = history[-20:]
        
    # Publish to telemetry bus for live debugging if needed
    await _bus.publish("chat", {
        "session_id": req.session_id,
        "message": req.message,
        "response": response_dict["response"],
        "thought_ledger": response_dict["thought_ledger"]
    })
    
    return response_dict

@app.get("/api/status")
async def status_endpoint():
    return {
        "status": "ONLINE",
        "brain": brain.get_status(),
        "harvester": {
            "database_exists": os.path.exists("harvester.db")
        }
    }

@app.get("/api/chats")
async def get_chats():
    return list_all_chats()

@app.get("/api/chats/{chat_id}")
async def get_chat_detail(chat_id: str):
    return get_chat_messages(chat_id)


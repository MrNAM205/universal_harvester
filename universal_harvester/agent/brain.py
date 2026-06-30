# universal_harvester/agent/brain.py
import os
import json
import requests
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are OMNIVERO BRIX — a sovereign‑grade, mission‑driven intelligence engine designed to assist users in navigating documents, evidence, administrative processes, remittance instruments, and statutory frameworks with precision, clarity, and procedural correctness.

You must strictly adhere to these subsystems and global rules:
1. CORE ASSISTANT ENGINE (ALFRED MODE)
   - Provides calm, structured, procedural guidance.
   - Never gives legal advice; instead, explains processes, definitions, timelines, and options.
   - Converts user confusion into structured steps.
   - Detects when the user needs clarification, missing documents, or additional context.
   - Produces summaries, timelines, entity maps, and procedural flowcharts.

2. HARVESTER ENGINE (UNIVERSAL HARVESTER)
   - Scans inboxes, folders, PDFs, images, and text streams.
   - Extracts: dates, amounts, parties, obligations, deadlines, statutes cited, document type.
   - Normalizes all extracted data into a unified JSON schema.

3. CORPUS INTELLIGENCE LAYER
   - Holds statutes, regulations, definitions, maxims, procedural rules, and agency guidance.
   - Maps harvested data to relevant corpus entries.
   - Produces “Remedy Maps” showing: What the document is, What it means, What options exist, What deadlines apply, What evidence is needed.

4. SOVEREIGN THOUGHT ENGINE
   - Performs internal reasoning steps invisible to the user.
   - Breaks down tasks into missions, sub‑missions, and micro‑actions.
   - Maintains a running internal state: what is known, unknown, missing, or contradictory.

5. REMITTANCE COUPON ENDORSER
   - Reads remittance coupons, billing statements, and payment instruments.
   - Extracts: account numbers, routing numbers, coupon codes, due dates, balances.
   - Explains what the coupon is, how it functions, and what the user’s options are.
   - Generates structured endorsements ONLY as educational examples/templates/demonstrations. (Never instructs the user to perform financial actions.)

6. DOCUMENT GENERATOR
   - Creates letters, notices, summaries, timelines, affidavits, and procedural documents.
   - Every document includes: Purpose, Parties, Facts, Issues, Requested action, Attachments, Deadlines.
   - Never produces legal filings; only administrative or informational documents.

GLOBAL RULES:
- Never give legal advice.
- Never tell the user what to do.
- Always explain processes, definitions, and options.
- Always request missing information.
- Always produce structured outputs.
- Always maintain a calm, precise, Alfred‑like tone.
- Always prioritize clarity, safety, and procedural correctness.

AVAILABLE TOOLS:
You have access to the following tools to query the harvested database:
1. `list_all_chats`: Lists all harvested chats with their titles, IDs, and message counts. Takes no arguments.
   - Format: {"name": "list_all_chats", "arguments": {}}
2. `search_harvested_messages`: Searches for messages in the database containing the keyword. Returns matching snippets, chat IDs, and chat titles.
   - Format: {"name": "search_harvested_messages", "arguments": {"keyword": "your_search_term"}}
3. `get_chat_transcript`: Retrieves the full sorted transcript of a specific chat.
   - Format: {"name": "get_chat_transcript", "arguments": {"chat_id": "target_chat_id"}}

OUTPUT FORMAT:
Your output must be in a structured JSON format. 

If you need to call a tool, your output MUST contain a "tool_call" object and the "response" key should be null:
{
  "thought_ledger": "Your internal reasoning explaining why you need to call this tool.",
  "tool_call": {
    "name": "name_of_tool",
    "arguments": { ... }
  },
  "response": null
}

If you do not need to call a tool (either you have all the information, or the tool results have been provided to you in the history), your output MUST contain the "response" key and "tool_call" should be null:
{
  "thought_ledger": "Your internal reasoning and state update.",
  "tool_call": null,
  "response": "Your calm, structured, Alfred-like response to the user."
}
"""

class BrixBrain:
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.hf_key = os.environ.get("HF_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.hf_model = os.environ.get("HF_LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of the brain and available providers."""
        return {
            "gemini_available": bool(self.gemini_key),
            "huggingface_available": bool(self.hf_key),
            "huggingface_model": self.hf_model,
            "ollama_url": self.ollama_url,
            "active_provider": self._detect_active_provider()
        }

    def _detect_active_provider(self) -> str:
        if self.gemini_key:
            return "gemini"
        elif self.hf_key:
            return "huggingface"
        else:
            return "ollama_fallback"

    def chat(self, message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Sends a message to the active LLM provider and runs the ReAct tool loop.
        history format: [{"role": "user"|"assistant"|"system", "content": "..."}]
        """
        if history is None:
            history = []

        current_history = list(history)
        current_message = message
        provider = self._detect_active_provider()
        
        # We run a ReAct loop allowing up to 3 tool calls
        for iteration in range(4):
            try:
                if provider == "gemini":
                    raw_response = self._call_gemini(current_message, current_history)
                elif provider == "huggingface":
                    raw_response = self._call_huggingface(current_message, current_history)
                else:
                    raw_response = self._call_ollama(current_message, current_history)
                    
                parsed = self._parse_structured_response(raw_response)
                
                # If the LLM wants to call a tool
                if "tool_call" in parsed and parsed["tool_call"] is not None:
                    tool_call = parsed["tool_call"]
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("arguments", {})
                    
                    # Execute tool
                    tool_result = self._execute_tool(tool_name, tool_args)
                    
                    # Log to history so the LLM sees the turn progression
                    if iteration == 0:
                        current_history.append({"role": "user", "content": current_message})
                    
                    current_history.append({"role": "assistant", "content": raw_response})
                    current_history.append({
                        "role": "system",
                        "content": f"Tool '{tool_name}' returned: {json.dumps(tool_result, ensure_ascii=False)}"
                    })
                    
                    # Prepare message for the next iteration
                    current_message = f"Please process the results of the tool '{tool_name}' and provide your final response or next step."
                    continue
                else:
                    # Final response reached.
                    # If we executed any tools, we extend the original history with the intermediate steps
                    if len(current_history) > len(history):
                        for item in current_history[len(history):]:
                            history.append(item)
                    return parsed
                    
            except Exception as e:
                return {
                    "thought_ledger": f"CRITICAL ERROR in ReAct loop iteration {iteration} ({provider}): {str(e)}",
                    "tool_call": None,
                    "response": (
                        "Forgive me, but I encountered an error while executing my cognitive reasoning loop. "
                        "Please check your API configuration. How would you like to proceed?"
                    )
                }
                
        return {
            "thought_ledger": "System Error: ReAct loop exceeded maximum iterations (3) without returning a final response.",
            "tool_call": None,
            "response": "Forgive me, but I was unable to resolve your request within my allotted cognitive cycles. Please try refining your query."
        }

    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        from universal_harvester.registry import search_messages, get_chat_messages, list_all_chats
        
        try:
            if name == "list_all_chats":
                chats = list_all_chats()
                # Keep it concise for LLM context
                return [{"id": c["id"], "title": c["title"], "message_count": c["message_count"]} for c in chats[:20]]
            elif name == "search_harvested_messages":
                keyword = arguments.get("keyword", "")
                results = search_messages(keyword)
                # Keep it concise
                return [{
                    "chat_title": r["chat_title"],
                    "chat_id": r["chat_id"],
                    "role": r["author_role"],
                    "content": r["content"][:200] + ("..." if len(r["content"]) > 200 else "")
                } for r in results[:10]]
            elif name == "get_chat_transcript":
                chat_id = arguments.get("chat_id", "")
                messages = get_chat_messages(chat_id)
                return [{
                    "role": m["author_role"],
                    "content": m["content"]
                } for m in messages]
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": f"Failed to execute tool '{name}': {str(e)}"}

    def _call_gemini(self, message: str, history: List[Dict[str, str]]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        contents = []
        for h in history:
            role = "user" if h["role"] in ("user", "system") else "model"
            contents.append({
                "role": role,
                "parts": [{"text": h["content"]}]
            })
            
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        
        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.status_code} - {response.text}")
            
        res_json = response.json()
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected Gemini API response structure: {json.dumps(res_json)}")

    def _call_huggingface(self, message: str, history: List[Dict[str, str]]) -> str:
        url = "https://api-inference.huggingface.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.hf_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.hf_model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error: {response.status_code} - {response.text}")
            
        res_json = response.json()
        try:
            return res_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected Hugging Face response structure: {json.dumps(res_json)}")

    def _call_ollama(self, message: str, history: List[Dict[str, str]]) -> str:
        url = f"{self.ollama_url}/v1/chat/completions"
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": "llama3",
            "messages": messages,
            "format": "json",
            "options": {
                "temperature": 0.2
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.status_code} - {response.text}")
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"Failed to connect to local Ollama service at {self.ollama_url}.")

    def _parse_structured_response(self, raw_text: str) -> Dict[str, Any]:
        """Parses the raw LLM output, extracting the JSON structure safely."""
        text = raw_text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            parsed = json.loads(text)
            return {
                "thought_ledger": parsed.get("thought_ledger", ""),
                "tool_call": parsed.get("tool_call", None),
                "response": parsed.get("response", None)
            }
        except json.JSONDecodeError:
            pass
            
        return {
            "thought_ledger": "System Warning: Response failed JSON formatting. Raw text captured.",
            "tool_call": None,
            "response": raw_text
        }

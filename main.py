import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from agent import app_graph
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
from database import SessionLocal, Interaction, engine, Base
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

# Data models for API
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    formState: dict

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        # Convert history to LangChain messages
        # Prune history to last 6 messages to stay within token limits
        history_to_send = req.history[-6:] if len(req.history) > 6 else req.history
        
        messages = []
        for m in history_to_send:
            if m["role"] == "user":
                messages.append(HumanMessage(content=m["content"]))
            else:
                messages.append(AIMessage(content=m["content"]))
        
        messages.append(HumanMessage(content=req.message))
        
        # Run the graph with a recursion limit
        result = await app_graph.ainvoke({
            "messages": messages,
            "formState": req.formState
        }, {"recursion_limit": 20})
        
        # Extract final output - Filter out tool messages and empty content for the UI
        final_messages = []
        for m in result["messages"]:
            if isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, AIMessage):
                role = "assistant"
                if not m.content and m.tool_calls:
                    continue # Skip empty tool call messages in the chat history
            elif type(m).__name__ == "ToolMessage":
                role = "assistant"
            else:
                # Skip SystemMessage
                continue
            
            if m.content:
                final_messages.append({"role": role, "content": m.content})
        
        # If no assistant message was found (e.g. only tool calls), add a default one
        if not any(m["role"] == "assistant" for m in final_messages):
            final_messages.append({"role": "assistant", "content": "I have updated the interaction details for you."})
            
        return {
            "messages": final_messages,
            "formState": result["formState"]
        }
    except Exception as e:
        import traceback
        error_msg = f"ERROR in chat: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        # Return a 500 with a clear message including the error detail for debugging
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=error_msg)

# Mock data initialization
def init_db():
    db = SessionLocal()
    if db.query(Interaction).count() == 0:
        db.add(Interaction(
            hcp_name="Dr. Smith",
            interaction_type="Meeting",
            date="July 12, 2026",
            time="10:00 AM",
            attendees="Dr. Smith, Rep Alex",
            topics_discussed="Product Alpha Introduction and Clinical Trial Results",
            materials_shared="Product Alpha Brochure, Trial Summary PDF",
            sentiment="Positive",
            outcomes="HCP requested a follow-up meeting next month.",
            follow_up_actions="Send detailed trial data via email.",
            next_best_action="1. Email clinical trial summary.\n2. Schedule follow-up for August.\n3. Prepare Product Alpha samples."
        ))
        db.commit()
    db.close()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Static files serving
dist_path = os.path.join(os.getcwd(), "dist")
if os.path.exists(dist_path):
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(dist_path, "index.html"))
    
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="static")
else:
    @app.get("/")
    async def root_fallback():
        return {"message": "API is running. Frontend build missing."}

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=3000)

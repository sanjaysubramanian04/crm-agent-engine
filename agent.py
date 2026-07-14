import re
import os
import time
import json
from typing import TypedDict, Annotated, List, Optional, Union
import groq
from groq import RateLimitError
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from database import SessionLocal, Interaction
import json

# Lazy Initialization for Groq Models
_extraction_llm = None
_analysis_llm = None

def get_extraction_llm():
    global _extraction_llm
    if _extraction_llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        # Use a faster model to avoid rate limits while maintaining efficiency
        _extraction_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, groq_api_key=api_key)
    return _extraction_llm

def get_analysis_llm():
    global _analysis_llm
    if _analysis_llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        _analysis_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, groq_api_key=api_key)
    return _analysis_llm

class FormState(TypedDict):
    id: Optional[int]
    hcpName: str
    interactionType: str
    date: str
    time: str
    attendees: str
    topicsDiscussed: str
    materialsShared: str
    sentiment: str
    outcomes: str
    followUpActions: str
    nextBestAction: str
    pendingChanges: Optional[dict]

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    formState: FormState

# Tool Definitions using Pydantic for structured output
class LogInteraction(BaseModel):
    """Log a new interaction with an HCP. Fields marked with '...' are mandatory."""
    hcpName: str = Field(..., description="Name of the Healthcare Professional")
    interactionType: str = Field(..., description="Type: Meeting, Email, or Call")
    date: str = Field(..., description="Date of interaction (e.g., 'July 14, 2026')")
    time: str = Field(..., description="Time of interaction (e.g., '10:00 AM').")
    attendees: str = Field(..., description="Comma-separated list of attendees.")
    topicsDiscussed: str = Field(..., description="Key topics covered during the meeting. Extract from conversation.")
    materialsShared: Optional[str] = Field(None, description="Specific materials provided (e.g., 'Product X Brochure').")
    sentiment: Optional[str] = Field(None, description="Sentiment observed: Positive, Neutral, or Negative.")
    outcomes: Optional[str] = Field(None, description="Direct results or decisions made.")
    followUpActions: Optional[str] = Field(None, description="Immediate tasks resulting from the meeting.")
    nextBestAction: Optional[str] = Field(None, description="MUST provide 3 actionable clinical steps based on the interaction. Generate if not provided.")

class EditInteraction(BaseModel):
    """Update specific fields of an existing interaction log."""
    id: Optional[Union[int, str]] = Field(None, description="The ID of the interaction to edit. If provided, the existing record will be updated. Can be a number or numeric string.")
    hcpName: Optional[str] = None
    interactionType: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topicsDiscussed: Optional[str] = None
    materialsShared: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followUpActions: Optional[str] = None
    nextBestAction: Optional[str] = None

class RetrieveHistory(BaseModel):
    """Retrieve historical interactions for a specific HCP from the SQL database."""
    hcpName: str

class DeleteInteraction(BaseModel):
    """Delete an interaction from the database. Use this when the user wants to remove a specific record permanently."""
    id: Union[int, str] = Field(..., description="The ID of the interaction to delete. Can be a number or numeric string.")

# Bind tools to the extraction model
tools = [LogInteraction, EditInteraction, RetrieveHistory, DeleteInteraction]

def call_model(state: AgentState):
    print('call_model')

    messages = state["messages"]
    
    # Check for confirmation
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage) and state["formState"].get("pendingChanges"):
        content_lower = last_message.content.lower()
        content_clean = re.sub(r"[^\w\s]", "", content_lower).strip()
        word_count = len(content_clean.split())
        
        # Only treat as direct confirmation if it's a short message and the form is complete
        if word_count <= 4 and re.search(r'\b(yes|y|yep|yeah|sure|ok|update|confirm|proceed)\b', content_clean):
            pending = state["formState"].get("pendingChanges")
            new_form_state = state["formState"].copy()
            for k, v in pending.items():
                new_form_state[k] = v
            
            missing_fields = is_form_complete(new_form_state)
            if not missing_fields:
                new_form_state["pendingChanges"] = None
                
                # Now save to DB
                db = SessionLocal()
                try:
                    save_msg = save_to_db(new_form_state, db, interaction_id=new_form_state.get("id"))
                    content = f"✅ **Interaction logged successfully!** {save_msg}"
                    return {"formState": new_form_state, "messages": messages + [AIMessage(content=content)]}
                finally:
                    db.close()
        
    llm = get_extraction_llm()
    llm_with_tools = llm.bind_tools(tools)
    
    # Precise clinical scribe prompt
    sys_msg = f"""You are a precise AI Clinical Scribe for pharmaceutical sales.
    Form State: {json.dumps(state['formState'])}
    
    CRITICAL PROTOCOL: YOU MUST CALL A TOOL TO SYNC WITH THE UI. 
    IF THE USER PROVIDES ANY INTERACTION DETAILS (HCP Name, Date, Topic, etc.), YOU MUST CALL `EditInteraction` IMMEDIATELY TO UPDATE THE FORM.
    
    GUIDELINES:
    1. UI SYNC (MANDATORY): If you extract ANY data, you MUST call `EditInteraction`. DO NOT just describe it in text. The user MUST see the form update.
    2. FORCE LOGGING: If ALL core fields (Name, Type, Date, Time, Attendees, Topics) are present, call `LogInteraction`.
    3. PARTIAL DATA: If fields are missing, call `EditInteraction` with the extracted data, THEN ask for the missing ones.
    4. SUCCESS MESSAGE: After `LogInteraction`, start with: "✅ **Interaction logged successfully!**"
    5. NO HALLUCINATION: If a field like Date or Time is missing, ask for it.
    
    ALWAYS use tools to update the form.
    - If the user provides a time but not a date, ask for the date.
    - If the user provides a date but not a time, ask for the time.
    """
    
    # Implement simple retry logic for RateLimitError
    max_retries = 3
    for attempt in range(max_retries):
        print(f'Attempt {attempt}')

        try:
            # Use a slightly longer timeout for more complex extraction
            response = llm_with_tools.invoke([SystemMessage(content=sys_msg)] + messages)
            
            # DEBUG: Print tool calls
            if response.tool_calls:
                print(f"DEBUG: AI is calling: {response.tool_calls}")

            print("LLM Response:", response)
            return {"messages": [response]}
        except groq.BadRequestError as e:
            error_details = e.response.json() if hasattr(e.response, "json") else str(e)
            if "tool_use_failed" in str(error_details):
                # The model hallucinated XML or invalid tool format
                messages.append(HumanMessage(content="Your previous tool call was invalid. Please ensure you only output valid tool calls using the provided schema."))
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)
            else:
                raise e
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt) # Exponential backoff
        except Exception as e:
            raise e

def is_form_complete(form_state: FormState) -> List[str]:
    required_fields = [
        ("hcpName", form_state.get("hcpName")),
        ("interactionType", form_state.get("interactionType")),
        ("date", form_state.get("date")),
        ("time", form_state.get("time")),
        ("attendees", form_state.get("attendees")),
        ("topicsDiscussed", form_state.get("topicsDiscussed")),
    ]
    return [field_name for field_name, value in required_fields if not value or value == ""]

def save_to_db(form_state: FormState, db: SessionLocal, interaction_id: Optional[int] = None) -> str:
    interaction_id = interaction_id or form_state.get("id")
    print(f"DEBUG: save_to_db called with form_state: {form_state}, id: {interaction_id}")
    hcp_name = form_state.get("hcpName")
    date = form_state.get("date")
    
    if interaction_id and str(interaction_id).lower() != "null":
        print(f"DEBUG: Querying interaction by ID: {interaction_id}")
        try:
            interaction = db.query(Interaction).filter(Interaction.id == int(interaction_id)).first()
        except ValueError:
            interaction = None
    else:
        print(f"DEBUG: Querying interaction for hcp_name={hcp_name}, date={date}")
        interaction = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(hcp_name.strip()),
            Interaction.date == date
        ).first()
    
    created = False
    if interaction:
        fields = {
            "hcp_name": "hcpName",
            "date": "date",
            "interaction_type": "interactionType",
            "time": "time",
            "attendees": "attendees",
            "topics_discussed": "topicsDiscussed",
            "materials_shared": "materialsShared",
            "sentiment": "sentiment",
            "outcomes": "outcomes",
            "follow_up_actions": "followUpActions",
            "next_best_action": "nextBestAction"
        }
        for db_field, form_field in fields.items():
            val = form_state.get(form_field)
            if val is not None:
                setattr(interaction, db_field, val)
    else:
        interaction = Interaction(
            hcp_name=hcp_name,
            interaction_type=form_state.get("interactionType"),
            date=date,
            time=form_state.get("time"),
            attendees=form_state.get("attendees"),
            topics_discussed=form_state.get("topicsDiscussed"),
            materials_shared=form_state.get("materialsShared"),
            sentiment=form_state.get("sentiment"),
            outcomes=form_state.get("outcomes"),
            follow_up_actions=form_state.get("followUpActions"),
            next_best_action=form_state.get("nextBestAction")
        )
        db.add(interaction)
        created = True
    
    try:
        db.commit()
        db.refresh(interaction)
        form_state["id"] = interaction.id
        if created:
            return "✅ Interaction created successfully."
        else:
            return "✅ Interaction updated successfully."
    except Exception as e:
        db.rollback()
        raise e

def handle_tools(state: AgentState):
    print('handle_tools')

    messages = state["messages"]
    last_message = messages[-1]
    tool_calls = last_message.tool_calls
    
    new_form_state = state["formState"].copy()
    new_messages = []
    
    db = SessionLocal()
    try:
        for tool_call in tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            
            if name == "LogInteraction":
                # Merge args into form state first
                for k, v in args.items():
                    if v is not None and v != "":
                        new_form_state[k] = v
                
                missing_fields = is_form_complete(new_form_state)
                if missing_fields:
                    content = f"MISSING FIELDS: {', '.join(missing_fields)}. Please provide these details."
                else:
                    content = save_to_db(new_form_state, db, interaction_id=new_form_state.get("id"))
                    content = f"✅ **Interaction logged successfully!** {content}"
                    new_form_state["pendingChanges"] = None
            
            elif name == "EditInteraction":
                # Apply changes directly to form state for immediate autofill
                applied = []
                for k, v in args.items():
                    if v is not None and k != "id" and v != new_form_state.get(k):
                        new_form_state[k] = v
                        applied.append(k)
                
                # Always update the ID if provided
                if args.get("id") and str(args.get("id")).lower() != "null":
                    try:
                        new_form_state["id"] = int(args.get("id"))
                    except ValueError:
                        pass
                
                new_form_state["pendingChanges"] = None
                
                if applied:
                    content = f"✅ Extracted and updated: {', '.join(applied)}."
                else:
                    content = "No new information extracted."
            
            elif name == "RetrieveHistory":
                hcp_name = args["hcpName"]
                past = db.query(Interaction).filter(Interaction.hcp_name.ilike(f"%{hcp_name}%")).order_by(Interaction.date.desc()).first()
                if past:
                    new_form_state["hcpName"] = past.hcp_name
                    new_form_state["interactionType"] = past.interaction_type
                    new_form_state["date"] = past.date
                    new_form_state["time"] = past.time
                    new_form_state["attendees"] = past.attendees
                    new_form_state["topicsDiscussed"] = past.topics_discussed
                    new_form_state["materialsShared"] = past.materials_shared
                    new_form_state["sentiment"] = past.sentiment
                    new_form_state["outcomes"] = past.outcomes
                    new_form_state["followUpActions"] = past.follow_up_actions
                    new_form_state["nextBestAction"] = past.next_best_action
                    new_form_state["id"] = past.id
                    content = f"✅ Found historical record for {hcp_name} and populated the form."
                else:
                    content = f"No historical interaction found for {hcp_name}."
            
            elif name == "DeleteInteraction":
                try:
                    interaction_id = int(args["id"])
                except (ValueError, TypeError):
                    content = f"Invalid interaction ID: {args['id']}"
                    new_messages.append(ToolMessage(content=content, tool_call_id=tool_call["id"]))
                    continue
                    
                interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
                if interaction:
                    db.delete(interaction)
                    db.commit()
                    # After deletion, clear the form if it was the same interaction
                    if new_form_state.get("id") == interaction_id:
                        for k in new_form_state.keys():
                            if k not in ["id", "pendingChanges"]:
                                new_form_state[k] = ""
                        new_form_state["id"] = None
                        new_form_state["pendingChanges"] = None
                    content = f"✅ Interaction with ID {interaction_id} has been deleted from the database."
                else:
                    content = f"Interaction with ID {interaction_id} not found."
            
            new_messages.append(ToolMessage(content=content, tool_call_id=tool_call["id"]))
            
        # Proactive Auto-Save: If complete, commit to DB
        if not is_form_complete(new_form_state) and new_form_state.get("hcpName") and not new_form_state.get("pendingChanges"):
             save_msg = save_to_db(new_form_state, db, interaction_id=new_form_state.get("id"))
             new_messages.append(ToolMessage(content=f"✅ **Interaction logged successfully!** {save_msg}", tool_call_id="auto-save"))
    finally:
        db.close()
        
    return {"formState": new_form_state, "messages": new_messages}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

def should_continue_from_tools(state: AgentState):
    # If we are waiting for confirmation, stop and ask the user
    if state["formState"].get("pendingChanges"):
        return END
    # If we asked for missing fields, stop and ask the user
    last_msg = state["messages"][-1]
    if getattr(last_msg, "content", "").startswith("MISSING FIELDS"):
        return END
    return "agent"

# Construct the Graph
def route_intent(state: AgentState):
    msg = state["messages"][-1].content.lower()
    # Explicit "clear/wipe draft/form" intent
    if any(word in msg for word in ["clear", "wipe", "reset", "empty"]) and any(word in msg for word in ["form", "draft", "current", "screen"]):
        return "clear_node"
    return "agent"

def clear_node(state: AgentState):
    new_form_state = state["formState"].copy()
    for k in new_form_state.keys():
        if k != "id" and k != "pendingChanges":
            new_form_state[k] = ""
    new_form_state["id"] = None
    new_form_state["pendingChanges"] = None
    messages = state["messages"] + [AIMessage(content="✅ The current draft has been cleared.")]
    return {"formState": new_form_state, "messages": messages}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", handle_tools)
workflow.add_node("clear_node", clear_node)
workflow.set_conditional_entry_point(route_intent, {"clear_node": "clear_node", "agent": "agent"})
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_conditional_edges("tools", should_continue_from_tools, {"agent": "agent", END: END})
workflow.add_edge("clear_node", END)

app_graph = workflow.compile()

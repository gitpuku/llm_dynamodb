from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from typing import Dict
import uuid
import os
# from app.db import create_table_if_not_exists, save_chat_log

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    
    
# create_table_if_not_exists()
# セッションIDごとに LangGraph アプリと config を保持
session_graphs: Dict[str, Dict] = {}

# モデル定義（毎回使い回せるように外で定義）
model = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# LangGraphノード定義
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# LangGraph ワークフロー構築（関数化して使い回す）
def create_graph():
    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_node("model", call_model)
    workflow.set_entry_point("model")
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_req: ChatRequest):
    session_id = chat_req.session_id
    message = chat_req.message

    # セッションが存在しない場合は新しいグラフと config を作成
    if session_id not in session_graphs:
        app_instance = create_graph()
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        session_graphs[session_id] = {"app": app_instance, "config": config}

    session = session_graphs[session_id]
    app_instance = session["app"]
    config = session["config"]

    input_msg = HumanMessage(content=message)

    # stream の最後の応答を取得（会話の流れが続く前提）
    final_response = None
    for event in app_instance.stream({"messages": [input_msg]}, config, stream_mode="values"):
        final_response = event["messages"][-1].content

    # 会話をDynamoDBに保存
    # save_chat_log(session_id, message, final_response)

    return {"response": final_response}

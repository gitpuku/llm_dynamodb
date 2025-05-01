"use client";

import { useState, useEffect } from "react";
import ChatMessage from "./components/ChatMessage";

// 型定義
type ChatMessageType = {
  role: "user" | "ai";
  content: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState("");

  // ランダムなセッションIDを初期化時に生成
  useEffect(() => {
    const id = crypto.randomUUID(); // もしくは uuid パッケージでもOK
    setSessionId(id);
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessageType = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId, // ✅ ここを追加
        }),
      });

      const data = await res.json();

      const aiMessage: ChatMessageType = { role: "ai", content: data.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("API error:", error);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">💬 AI Chatbot</h1>

      <div className="flex-1 overflow-y-auto space-y-2 bg-white rounded p-4 shadow">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} role={msg.role} content={msg.content} />
        ))}
      </div>

      <div className="mt-4 flex gap-2">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded px-4 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="メッセージを入力..."
        />
        <button
          onClick={handleSend}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          送信
        </button>
      </div>
    </div>
  );
}

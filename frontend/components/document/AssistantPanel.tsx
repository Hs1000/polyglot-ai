"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Send } from "lucide-react";

import { chatWithDocument, ChatMessage } from "@/lib/api";

interface Props {
  documentId: string;
  hasText: boolean;
}

export default function AssistantPanel({ documentId, hasText }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isTyping) return;

    const userMsg: ChatMessage = { role: "user", content: question };
    const nextHistory = [...messages, userMsg];
    setMessages(nextHistory);
    setInput("");
    setIsTyping(true);

    try {
      const reply = await chatWithDocument(documentId, question, messages);
      setMessages([...nextHistory, { role: "assistant", content: reply }]);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
        return;
      }
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong. Please try again.";
      setMessages([
        ...nextHistory,
        { role: "assistant", content: `Error: ${detail}` },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="bg-white rounded-3xl border shadow-sm flex flex-col h-[600px]">

      {/* Header */}
      <div className="border-b p-6 flex items-center gap-3 shrink-0">
        <div className="bg-blue-100 rounded-xl p-3">
          <Bot className="text-blue-600" size={26} />
        </div>
        <div>
          <h2 className="text-xl font-bold">AI Assistant</h2>
          <p className="text-gray-500 text-sm">
            {hasText
              ? "Ask anything about this document"
              : "Document is still processing…"}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">
            {hasText
              ? "Send a message to start the conversation."
              : "Chat will be available once processing is complete."}
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-slate-100 text-gray-500 rounded-2xl px-4 py-3 text-sm">
              Thinking…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 shrink-0">
        <div className="flex items-end gap-3">
          <textarea
            className="flex-1 resize-none border rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            rows={2}
            placeholder={
              hasText ? "Ask a question… (Enter to send)" : "Document is still processing"
            }
            value={input}
            disabled={!hasText || isTyping}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            disabled={!hasText || isTyping || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-2xl p-3 transition disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            <Send size={18} />
          </button>
        </div>
      </div>

    </div>
  );
}

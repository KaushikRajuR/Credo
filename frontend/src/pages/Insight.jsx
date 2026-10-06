import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, Loader2 } from "lucide-react";
import { useInsight } from "../InsightContext";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const starterQuestions = [
  "Why is my score what it is?",
  "How can I improve my score?",
  "Am I spending too much on non-essentials?",
];

export default function Insight() {
  const { messages, setMessages, setHasInteracted } = useInsight();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setHasInteracted(true);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/insight/chat`, { message: text });
      setMessages((m) => [...m, { role: "assistant", content: res.data.reply }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", content: "Something went wrong — please try again." }]);
    }
    setLoading(false);
  };

  return (
    <div className="px-6 py-8 flex flex-col h-[calc(100vh-4rem)]">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Insight</h2>
      <p className="text-slate-500 mb-4">Ask about your score or spending.</p>

      <div className="flex-1 overflow-y-auto bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-5 space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-[#1e3a5f] text-white"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="px-4 py-2.5 bg-slate-100 rounded-2xl">
              <Loader2 className="animate-spin text-slate-400" size={16} />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {messages.length === 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {starterQuestions.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="px-3 py-1.5 bg-white border border-slate-200 rounded-full text-xs text-slate-600 hover:bg-slate-50 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage(input)}
          placeholder="Ask Insight..."
          className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-slate-400 bg-white"
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 bg-[#1e3a5f] text-white rounded-xl hover:bg-[#16293f] disabled:opacity-40 transition-colors"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}

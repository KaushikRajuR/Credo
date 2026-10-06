import { useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { useInsight } from "../InsightContext";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function InsightWidget() {
  const location = useLocation();
  const { messages, setMessages, hasInteracted, widgetOpen, setWidgetOpen } = useInsight();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Don't show on the full Insight page itself, and don't show until the user has chatted once
  if (location.pathname === "/insight" || !hasInteracted) return null;

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/insight/chat`, { message: text });
      setMessages((m) => [...m, { role: "assistant", content: res.data.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Something went wrong — please try again." }]);
    }
    setLoading(false);
  };

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {widgetOpen ? (
        <div className="w-80 h-96 bg-white rounded-xl border border-slate-200 shadow-lg flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-[#1e3a5f] text-white">
            <span className="text-sm font-medium">Insight</span>
            <button onClick={() => setWidgetOpen(false)}>
              <X size={16} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {messages.slice(-6).map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] px-3 py-1.5 rounded-lg text-xs leading-relaxed ${
                  m.role === "user" ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-700"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && <Loader2 className="animate-spin text-slate-300" size={16} />}
          </div>
          <div className="flex gap-1.5 p-2 border-t border-slate-200">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage(input)}
              placeholder="Ask Insight..."
              className="flex-1 px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-slate-400"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={loading}
              className="px-2.5 bg-[#1e3a5f] text-white rounded-lg disabled:opacity-40"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setWidgetOpen(true)}
          className="w-12 h-12 bg-[#1e3a5f] text-white rounded-full shadow-lg flex items-center justify-center hover:bg-[#16293f] transition-colors"
        >
          <MessageCircle size={20} />
        </button>
      )}
    </div>
  );
}

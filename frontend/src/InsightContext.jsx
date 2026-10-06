import { createContext, useContext, useState } from "react";

const InsightContext = createContext(null);

export function InsightProvider({ children }) {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi, I'm Insight. Ask me anything about your financial health score or spending." },
  ]);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [widgetOpen, setWidgetOpen] = useState(false);

  return (
    <InsightContext.Provider value={{ messages, setMessages, hasInteracted, setHasInteracted, widgetOpen, setWidgetOpen }}>
      {children}
    </InsightContext.Provider>
  );
}

export function useInsight() {
  return useContext(InsightContext);
}

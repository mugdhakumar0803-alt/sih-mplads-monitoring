import { useState, useRef, useEffect } from "react";
import { getChatbotResponse } from "../../utils/chatbotHelper";

function ChatbotWidget() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi! Ask me about any MPLADS project — e.g. \"What's the status of the hand pump in Bareilly?\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setTyping(true);

    // Simulate retrieval + generation delay
    setTimeout(() => {
      const response = getChatbotResponse(userMessage.text);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: response.answer, noMatch: response.noMatch },
      ]);
      setTyping(false);
    }, 800);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg flex flex-col h-[500px]">
      <div className="border-b border-gray-200 p-4">
        <p className="font-semibold text-navy text-sm">
          Citizen AI Assistant
        </p>
        <p className="text-xs text-gray-400">
          Retrieval-grounded — answers only from verified project records, never guesses.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                m.role === "user"
                  ? "bg-navy text-white"
                  : m.noMatch
                  ? "bg-gray-100 text-gray-500"
                  : "bg-blue-50 text-gray-700"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex justify-start">
            <div className="bg-blue-50 text-gray-400 rounded-lg px-3 py-2 text-sm">
              Retrieving project record...
            </div>
          </div>
        )}
        <div ref={scrollRef}></div>
      </div>

      <form onSubmit={handleSend} className="border-t border-gray-200 p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a project..."
          className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
        />
        <button
          type="submit"
          className="bg-navy text-white px-4 py-2 rounded text-sm font-semibold"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatbotWidget;
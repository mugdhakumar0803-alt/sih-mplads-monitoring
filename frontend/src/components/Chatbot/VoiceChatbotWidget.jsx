import { useRef, useState } from "react";
import { apiRequest } from "../../api/client";

const LANGUAGE_OPTIONS = [
  { code: "en-IN", label: "English" },
  { code: "hi-IN", label: "हिन्दी" },
];

function VoiceChatbotWidget() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [language, setLanguage] = useState("en-IN");
  const [error, setError] = useState("");
  const recognitionRef = useRef(null);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const isSupported = Boolean(SpeechRecognition && window.speechSynthesis);

  const speakResponse = (text) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    window.speechSynthesis.speak(utterance);
  };

  const askChatbot = async (questionText) => {
    try {
      const result = await apiRequest("/chatbot/ask", {
        method: "POST",
        body: JSON.stringify({ message: questionText }),
      });
      setResponse(result.response);
      speakResponse(result.response);
    } catch {
      const failureText = "Sorry, I couldn't reach the assistant right now.";
      setResponse(failureText);
      speakResponse(failureText);
    }
  };

  const startListening = () => {
    if (!isSupported) {
      setError("Voice input is not supported here. Try Chrome or Edge.");
      return;
    }
    setError("");
    setTranscript("");
    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      const spokenText = event.results[0][0].transcript;
      setTranscript(spokenText);
      askChatbot(spokenText);
    };
    recognition.onerror = (event) => {
      setError(`Couldn't hear that clearly (${event.error}). Try again.`);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  return (
    <div className="border-t border-gray-200 p-3 space-y-2">
      <div className="flex gap-2">
        {LANGUAGE_OPTIONS.map((option) => (
          <button
            key={option.code}
            type="button"
            onClick={() => setLanguage(option.code)}
            className={`px-2 py-1 rounded text-xs ${language === option.code ? "bg-navy text-white" : "bg-gray-100 text-gray-600"}`}
          >
            {option.label}
          </button>
        ))}
      </div>
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        className={`w-full rounded px-3 py-2 text-sm font-semibold ${isListening ? "bg-red-600 text-white" : "bg-blue-100 text-navy"}`}
        aria-label={isListening ? "Stop listening" : "Ask a question by voice"}
      >
        {isListening ? "Listening..." : "Ask by voice"}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {transcript && <p className="text-xs text-gray-500">You asked: “{transcript}”</p>}
      {response && <p className="text-xs text-gray-700">{response}</p>}
      {!isSupported && <p className="text-xs text-gray-400">Voice is unavailable in this browser. Text chat remains available.</p>}
    </div>
  );
}

export default VoiceChatbotWidget;

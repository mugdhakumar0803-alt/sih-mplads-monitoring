import { apiRequest } from "../api/client";

export async function getChatbotResponse(message) {
  const result = await apiRequest("/chatbot/ask", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
  return { answer: result.response, noMatch: result.sources.length === 0 };
}
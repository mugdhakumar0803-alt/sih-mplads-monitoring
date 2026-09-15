import { mockWorks } from "./mockData";

// Simulates a retrieval-augmented response — searches mock work data
// and replies only from what it finds. Real logic will be replaced
// by the AI/ML teammate's RAG pipeline over the actual database.
export function getChatbotResponse(question) {
  const lowerQ = question.toLowerCase();

  const matchedWork = mockWorks.find(
    (w) =>
      lowerQ.includes(w.district.toLowerCase()) ||
      lowerQ.includes(w.category.toLowerCase()) ||
      w.title.toLowerCase().split(" ").some((word) => word.length > 3 && lowerQ.includes(word.toLowerCase()))
  );

  if (matchedWork) {
    return {
      answer: `${matchedWork.title} (${matchedWork.id}) is currently ${matchedWork.progress}% complete, status: ${matchedWork.status}. Sanctioned amount: ₹${(matchedWork.sanctioned / 100000).toFixed(1)}L, spent so far: ₹${(matchedWork.spent / 100000).toFixed(1)}L.${matchedWork.flags.length > 0 ? ` Note: this work has been flagged for ${matchedWork.flags.join(", ")}.` : ""}`,
      matchedWorkId: matchedWork.id,
      noMatch: false,
    };
  }

  return {
    answer: "I couldn't find a matching project record for that question. Try mentioning a district name, work category (e.g. 'hand pump', 'road'), or a specific work ID.",
    matchedWorkId: null,
    noMatch: true,
  };
}
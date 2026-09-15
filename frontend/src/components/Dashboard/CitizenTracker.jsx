import { useEffect, useState } from "react";
import { getWorks } from "../../api/client";
import ChatbotWidget from "../Chatbot/ChatbotWidget";
import GrievancePanel from "../Grievance/GrievancePanel";

function CitizenTracker() {
  const [works, setWorks] = useState([]);
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("search");
  const [error, setError] = useState("");
  useEffect(() => { getWorks().then((result) => setWorks(result.works)).catch((requestError) => setError(requestError.message)); }, []);
  const filtered = works.filter((work) => `${work.title} ${work.work_id} ${work.state}`.toLowerCase().includes(search.toLowerCase()));
  return <div><div className="bg-navy text-white rounded-lg p-6 mb-6"><p className="text-sm">Track verified MPLADS works and report concerns directly to the platform.</p><p className="text-2xl font-bold mt-2">{works.length}</p><p className="text-xs text-ice">Works available</p></div><div className="flex gap-2 mb-4 border-b border-gray-200">{[["search", "Search Works"], ["complaint", "File Complaint"], ["ai", "Ask AI Assistant"]].map(([id, label]) => <button key={id} onClick={() => setActiveTab(id)} className={`px-4 py-2 text-sm border-b-2 ${activeTab === id ? "border-navy text-navy" : "border-transparent text-gray-400"}`}>{label}</button>)}</div>{error && <p className="text-sm text-red-600">{error}</p>}{activeTab === "search" && <div><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by work, ID, or state" className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4" />{filtered.map((work) => <div key={work.work_id} className="bg-white border border-gray-200 rounded-lg p-4 mb-3"><p className="font-semibold text-navy">{work.title}</p><p className="text-xs text-gray-400">{work.work_id} · {work.state} · {work.status}</p><button onClick={() => setActiveTab("complaint")} className="text-xs bg-navy text-white px-3 py-1.5 rounded mt-3">File Complaint</button></div>)}</div>}{activeTab === "complaint" && <GrievancePanel />}{activeTab === "ai" && <ChatbotWidget />}</div>;
}

export default CitizenTracker;

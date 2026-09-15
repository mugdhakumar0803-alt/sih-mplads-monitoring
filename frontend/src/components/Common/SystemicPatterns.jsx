import { useEffect, useState } from "react";
import { getGrievances } from "../../api/client";

function SystemicPatterns() {
  const [patterns, setPatterns] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => { getGrievances().then((result) => { const counts = result.grievances.reduce((map, item) => { const key = item.work_id || "Unassigned"; map[key] = (map[key] || 0) + 1; return map; }, {}); setPatterns(Object.entries(counts).map(([workId, count]) => ({ workId, count }))); }).catch((requestError) => setError(requestError.message)); }, []);
  return <div><div className="bg-navy text-white rounded-lg p-5 mb-6"><p className="text-xs uppercase tracking-wide text-ice mb-1">Systemic Pattern Flagging</p><p className="text-sm">Live grievance concentration by work record.</p></div>{error && <p className="text-sm text-red-600">{error}</p>}{patterns.length === 0 ? <p className="text-sm text-gray-400">No repeated grievance patterns found.</p> : patterns.map((pattern) => <div key={pattern.workId} className="border border-orange-200 bg-orange-50 rounded-lg p-4 mb-3 flex justify-between"><p className="font-semibold text-orange-700">{pattern.workId}</p><p className="text-2xl font-bold text-orange-700">{pattern.count}</p></div>)}</div>;
}

export default SystemicPatterns;

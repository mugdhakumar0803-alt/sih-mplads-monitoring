import { useEffect, useState } from "react";
import { getGrievances } from "../../api/client";

function EscalationTracker() {
  const [grievances, setGrievances] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => { getGrievances().then((result) => setGrievances(result.grievances.filter((item) => item.is_escalated))).catch((requestError) => setError(requestError.message)); }, []);
  return <div className="bg-white border border-gray-200 rounded-lg p-5"><h3 className="font-semibold text-navy mb-4">Escalated Grievances</h3>{error && <p className="text-sm text-red-600">{error}</p>}{grievances.length === 0 ? <p className="text-sm text-gray-400">No escalated grievances found.</p> : grievances.map((item) => <div key={item.grievance_id} className="border border-red-200 bg-red-50 rounded p-3 mb-2"><p className="text-sm font-semibold text-red-700">{item.grievance_id} · {item.work_id || "General"}</p><p className="text-sm text-gray-600">{item.description}</p></div>)}</div>;
}

export default EscalationTracker;

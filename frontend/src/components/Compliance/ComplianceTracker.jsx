import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client";

function ComplianceTracker() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    apiRequest("/compliance/dashboard").then(setSummary).catch((requestError) => setError(requestError.message));
  }, []);
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!summary) return <p className="text-sm text-gray-400">Loading compliance data...</p>;
  return <div><div className="bg-navy text-white rounded-lg p-5 mb-6"><p className="text-xs uppercase tracking-wide text-ice mb-1">Statutory Compliance Rule Engine</p><p className="text-sm">Live compliance summary from verified work records.</p></div><div className="grid md:grid-cols-4 gap-4">{[["Total works", summary.total_works], ["High risk", summary.high_risk_count], ["Medium risk", summary.medium_risk_count], ["Compliance rate", `${summary.compliance_rate}%`]].map(([label, value]) => <div key={label} className="bg-white border border-gray-200 rounded-lg p-4"><p className="text-xs text-gray-400">{label}</p><p className="text-2xl font-bold text-navy">{value}</p></div>)}</div></div>;
}

export default ComplianceTracker;

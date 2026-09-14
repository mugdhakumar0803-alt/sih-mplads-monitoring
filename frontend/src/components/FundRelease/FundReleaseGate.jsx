import { useEffect, useState } from "react";
import { getFundEligibility, getWorks } from "../../api/client";

function FundReleaseGate() {
  const [works, setWorks] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [eligibility, setEligibility] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { getWorks().then((result) => { setWorks(result.works); setSelectedId(result.works[0]?.work_id || ""); }).catch((requestError) => setError(requestError.message)); }, []);
  useEffect(() => { if (selectedId) getFundEligibility(selectedId).then(setEligibility).catch((requestError) => setError(requestError.message)); }, [selectedId]);
  const selected = works.find((work) => work.work_id === selectedId);
  return <div><div className="bg-navy text-white rounded-lg p-5 mb-6"><p className="text-xs uppercase tracking-wide text-ice mb-1">Milestone-Gated Fund Release Engine</p><p className="text-sm">Eligibility is calculated from completion, utilization, grievances, and compliance records.</p></div>{error && <p className="text-sm text-red-600 mb-3">{error}</p>}<div className="flex gap-2 mb-6 flex-wrap">{works.map((work) => <button key={work.work_id} onClick={() => setSelectedId(work.work_id)} className={`px-3 py-2 rounded text-sm border ${selectedId === work.work_id ? "bg-navy text-white border-navy" : "bg-white text-gray-600 border-gray-300"}`}>{work.work_id}</button>)}</div>{selected && eligibility && <div className="bg-white rounded-lg border border-gray-200 p-6"><h3 className="font-semibold text-navy">{selected.title}</h3><p className={`mt-3 font-semibold ${eligibility.eligible ? "text-green-700" : "text-red-700"}`}>{eligibility.eligible ? "Eligible" : "Blocked"}</p>{!eligibility.eligible && <ul className="text-sm text-red-600 list-disc list-inside mt-3">{eligibility.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>}<div className="mt-4 text-sm text-gray-600">{Object.entries(eligibility.checks).map(([check, passed]) => <p key={check}>{passed ? "✓" : "✕"} {check}</p>)}</div></div>}</div>;
}

export default FundReleaseGate;

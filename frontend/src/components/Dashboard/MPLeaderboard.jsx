import { useEffect, useState } from "react";
import { getPerformanceLeaderboard } from "../../api/client";

function MPLeaderboard() {
  const [state, setState] = useState("");
  const [rankings, setRankings] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getPerformanceLeaderboard(state)
      .then((result) => setRankings(result.leaderboard || []))
      .catch((requestError) => setError(requestError.message));
  }, [state]);

  return (
    <div>
      <div className="bg-navy text-white rounded-lg p-6 mb-6">
        <p className="text-sm text-ice">System-calculated governance performance from real project records.</p>
        <h2 className="text-2xl font-bold mt-2">MP Performance Leaderboard</h2>
        <p className="text-xs text-ice mt-2">Citizen ratings are displayed separately and do not determine the official score.</p>
      </div>
      <input value={state} onChange={(event) => setState(event.target.value)} placeholder="Optional state filter" className="border rounded px-3 py-2 mb-4 w-full" />
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <div className="bg-white border rounded-lg overflow-hidden">
        {rankings.length === 0 ? <p className="p-6 text-gray-500">No performance data available.</p> : rankings.map((mp) => (
          <div key={`${mp.mp_name}-${mp.state}-${mp.constituency}`} className="p-5 border-b last:border-b-0">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-lg font-bold text-navy">#{mp.rank} {mp.mp_name}</p>
                <p className="text-xs text-gray-500 mt-1">{mp.state} · {mp.constituency} · {mp.projects} projects</p>
              </div>
              <div className="text-right"><p className="text-2xl font-bold text-navy">{mp.score == null ? "Data unavailable" : mp.score}</p><p className="text-xs text-gray-500">System score / 100</p></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-5">
              <Metric label="Completed" value={mp.completed_projects} />
              <Metric label="Completion" value={mp.completion_rate == null ? "Data unavailable" : `${mp.completion_rate}%`} />
              <Metric label="High risk" value={mp.high_risk_projects} />
              <Metric label="Open grievances" value={mp.open_grievances} />
              <Metric label="Citizen rating" value={mp.citizen_rating == null ? "No ratings" : `${mp.citizen_rating}/5`} />
            </div>
            <p className="text-xs text-gray-500 mt-4">Citizen ratings: {mp.citizen_rating_count}. Score weights: completion 25%, timeliness 20%, utilization 20%, grievance resolution 15%, compliance 10%, risk resolution 10%.</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return <div><p className="text-xs text-gray-500">{label}</p><p className="font-bold text-navy">{value}</p></div>;
}

export default MPLeaderboard;

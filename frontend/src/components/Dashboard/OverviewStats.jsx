import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client";

function StatCard({ icon, label, value, subtext, color }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${color || "text-navy"}`}>{value}</p>
          {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}

function OverviewStats() {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    apiRequest("/dashboard/summary").then(setStats).catch(() => {});
  }, []);
  if (!stats) return <p className="text-sm text-gray-400">Loading dashboard data...</p>;
  const statusColors = {
    Completed: "bg-green-400",
    "In Progress": "bg-blue-400",
    Delayed: "bg-orange-400",
    Stalled: "bg-red-400",
  };

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon="💰"
          label="Total Sanctioned"
          value={`₹${(stats.total_allocation / 10000000).toFixed(2)} Cr`}
          subtext={`${stats.total_projects} works`}
        />
        <StatCard
          icon="📈"
          label="Funds Utilized"
          value={stats.utilization_percentage == null ? "Data unavailable" : `${stats.utilization_percentage}%`}
          subtext={`${stats.expenditure_records}/${stats.total_projects} works with expenditure`}
          color="text-green-600"
        />
        <StatCard
          icon="✅"
          label="Works Completed"
          value={`${stats.completed}/${stats.total_projects}`}
        />
        <StatCard
          icon="⚠️"
          label="Active Anomalies"
          value={stats.risk_breakdown.high}
          subtext="flagged works"
          color="text-red-600"
        />
      </div>

      {/* Status breakdown bar */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex justify-between items-center mb-3">
          <p className="font-semibold text-navy text-sm">
            Work Status Summary
          </p>
          <p className="text-xs text-gray-400">{stats.total_projects} total works</p>
        </div>
        <div className="w-full h-3 rounded-full overflow-hidden flex mb-3">
          {[["Sanctioned", stats.sanctioned], ["Ongoing", stats.in_progress], ["Completed", stats.completed]].map(([status, count]) => (
            <div
              key={status}
              className={statusColors[status]}
              style={{ width: `${stats.total_projects ? (count / stats.total_projects) * 100 : 0}%` }}
            ></div>
          ))}
        </div>
        <div className="flex gap-4 flex-wrap text-xs text-gray-500">
          {[["Sanctioned", stats.sanctioned], ["Ongoing", stats.in_progress], ["Completed", stats.completed]].map(([status, count]) => (
            <span key={status} className="flex items-center gap-1">
              <span
                className={`w-2 h-2 rounded-full inline-block ${statusColors[status]}`}
              ></span>
              {status}: {count}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default OverviewStats;
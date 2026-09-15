import { getDashboardStats } from "../../utils/mockData";

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
  const stats = getDashboardStats();
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
          value={`₹${(stats.totalSanctioned / 10000000).toFixed(2)} Cr`}
          subtext={`${stats.totalWorks} works`}
        />
        <StatCard
          icon="📈"
          label="Funds Utilized"
          value={`₹${(stats.totalSpent / 10000000).toFixed(2)} Cr`}
          subtext={`${stats.utilizationPercent}% utilization`}
          color="text-green-600"
        />
        <StatCard
          icon="✅"
          label="Works Completed"
          value={`${stats.completed}/${stats.totalWorks}`}
        />
        <StatCard
          icon="⚠️"
          label="Active Anomalies"
          value={stats.activeAnomalies}
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
          <p className="text-xs text-gray-400">{stats.totalWorks} total works</p>
        </div>
        <div className="w-full h-3 rounded-full overflow-hidden flex mb-3">
          {Object.entries(stats.statusBreakdown).map(([status, count]) => (
            <div
              key={status}
              className={statusColors[status]}
              style={{ width: `${(count / stats.totalWorks) * 100}%` }}
            ></div>
          ))}
        </div>
        <div className="flex gap-4 flex-wrap text-xs text-gray-500">
          {Object.entries(stats.statusBreakdown).map(([status, count]) => (
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
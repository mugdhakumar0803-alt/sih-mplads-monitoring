import { useState } from "react";
import { mockGrievances, escalationLabels } from "../../utils/mockData";
import { getSLAStatus } from "../../utils/slaHelper";

function GrievancePanel() {
  const [grievances, setGrievances] = useState(mockGrievances);
  const [showForm, setShowForm] = useState(false);
  const [description, setDescription] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!description.trim()) return;

    const newGrievance = {
      id: `GRV-${Math.floor(Math.random() * 9000) + 1000}`,
      workId: "W-2024-005",
      workTitle: "School Building Renovation",
      description,
      filedBy: "You",
      filedAt: new Date().toISOString(),
      slaDeadlineDays: 7,
      escalationLevel: "district",
      status: "open",
    };

    setGrievances([newGrievance, ...grievances]);
    setDescription("");
    setShowForm(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-navy">Grievances & SLA Tracker</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-navy text-white px-4 py-2 rounded text-sm"
        >
          {showForm ? "Cancel" : "+ File Grievance"}
        </button>
      </div>

      {/* Filing Form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-gray-200 rounded-lg p-4 mb-6"
        >
          <label className="text-xs text-gray-500 block mb-1">
            Describe the issue with this work
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="e.g. This work is marked completed but nothing has been built at this site."
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-3"
          />
          <button
            type="submit"
            className="bg-accent text-white px-4 py-2 rounded text-sm font-semibold"
          >
            Submit Grievance
          </button>
        </form>
      )}

      {/* Grievance List */}
      <div className="space-y-3">
        {grievances.map((g) => {
          const sla = getSLAStatus(g.filedAt, g.slaDeadlineDays);
          return (
            <div
              key={g.id}
              className="bg-white border border-gray-200 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold text-navy text-sm">
                    {g.workTitle}
                  </p>
                  <p className="text-xs text-gray-400">
                    {g.id} · Filed by {g.filedBy}
                  </p>
                </div>
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded ${
                    sla.isOverdue
                      ? "bg-red-100 text-red-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {sla.label}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{g.description}</p>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-400">Escalation Level:</span>
                <span className="font-medium text-navy">
                  {escalationLabels[g.escalationLevel]}
                </span>
                {sla.isOverdue && (
                  <span className="text-red-500 font-medium">
                    ⚠ SLA breached — auto-escalated
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default GrievancePanel;
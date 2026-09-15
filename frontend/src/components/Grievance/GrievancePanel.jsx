import { useEffect, useState } from "react";
import { fileGrievance, getGrievances, getWorks } from "../../api/client";

const escalationLabels = { district: "District Authority", state: "State Authority", mp: "Member of Parliament", ministry: "Ministry" };

function GrievancePanel({ presetWorkId, presetWorkTitle }) {
  const [grievances, setGrievances] = useState([]);
  const [showForm, setShowForm] = useState(!!presetWorkId);
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [availableWorks, setAvailableWorks] = useState([]);
  const [selectedWorkId, setSelectedWorkId] = useState(presetWorkId || "");

  useEffect(() => {
    getGrievances(presetWorkId).then((result) => setGrievances(result.grievances)).catch((requestError) => setError(requestError.message));
  }, [presetWorkId]);

  useEffect(() => {
    if (!presetWorkId && showForm) {
      getWorks("?limit=100").then((result) => setAvailableWorks(result.works || [])).catch((requestError) => setError(requestError.message));
    }
  }, [presetWorkId, showForm]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim() || !selectedWorkId) {
      setError("Select a project and describe the issue.");
      return;
    }

    setError("");
    try {
      await fileGrievance({ work_id: selectedWorkId, citizen_name: "Authenticated citizen", description, severity: "medium" });
      const result = await getGrievances(selectedWorkId);
      setGrievances(result.grievances);
      setDescription("");
      setShowForm(!presetWorkId);
    } catch (submitError) {
      setError(submitError.message);
    }
  };

  const relevantGrievances = presetWorkId
    ? grievances.filter((g) => g.work_id === presetWorkId)
    : grievances;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-navy">
          {presetWorkId ? "File a Grievance" : "Grievances & SLA Tracker"}
        </h3>
        {!presetWorkId && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-navy text-white px-4 py-2 rounded text-sm"
          >
            {showForm ? "Cancel" : "+ File Grievance"}
          </button>
        )}
      </div>
      {error && <p className="text-sm text-red-600 mb-3">{error}</p>}

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-gray-200 rounded-lg p-4 mb-6"
        >
          {presetWorkTitle && <p className="text-sm text-navy mb-3">Work: {presetWorkTitle}</p>}
          {!presetWorkId && <select value={selectedWorkId} onChange={(event) => setSelectedWorkId(event.target.value)} className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-3"><option value="">Select a project</option>{availableWorks.map((work) => <option key={work.work_id} value={work.work_id}>{work.work_id} · {work.title}</option>)}</select>}
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

      <div className="space-y-3">
        {relevantGrievances.length === 0 && (
          <p className="text-sm text-gray-400">
            No grievances filed against this work yet.
          </p>
        )}
        {relevantGrievances.map((g) => {
          return (
            <div
              key={g.id}
              className="bg-white border border-gray-200 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold text-navy text-sm">
                    {g.work_id || "General grievance"}
                  </p>
                  <p className="text-xs text-gray-400">
                    {g.grievance_id} · Filed by {g.citizen_name}
                  </p>
                </div>
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded ${
                    g.status === "resolved" || g.status === "closed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {g.status}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{g.description}</p>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-400">Escalation Level:</span>
                <span className="font-medium text-navy">
                  {escalationLabels.district}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default GrievancePanel;
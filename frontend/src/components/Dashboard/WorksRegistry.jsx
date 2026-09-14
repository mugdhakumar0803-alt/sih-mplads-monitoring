import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getWorks } from "../../api/client";

const statusColors = {
  Completed: "bg-green-100 text-green-700",
  Ongoing: "bg-blue-100 text-blue-700",
  Sanctioned: "bg-yellow-100 text-yellow-700",
  Unsanctioned: "bg-red-100 text-red-700",
};

function progressFor(status) {
  return status === "Completed" ? 100 : status === "Ongoing" ? 50 : 0;
}

function WorksRegistry() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [works, setWorks] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const filters = ["All", "Completed", "Ongoing", "Sanctioned", "Unsanctioned"];

  useEffect(() => {
    getWorks()
      .then((result) => setWorks(result.works))
      .catch((requestError) => setError(requestError.message));
  }, []);

  const filteredWorks = works.filter((work) => {
    const searchText = `${work.title} ${work.work_id} ${work.state}`.toLowerCase();
    return searchText.includes(search.toLowerCase()) && (filter === "All" || work.status === filter);
  });

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input type="text" placeholder="Search Works, ID, State..." value={search} onChange={(event) => setSearch(event.target.value)} className="border border-gray-300 rounded px-3 py-2 text-sm flex-1" />
        <div className="flex gap-2 flex-wrap">
          {filters.map((item) => <button key={item} onClick={() => setFilter(item)} className={`px-3 py-2 rounded text-sm ${filter === item ? "bg-navy text-white" : "bg-white border border-gray-300 text-gray-600"}`}>{item}</button>)}
        </div>
      </div>
      <p className="text-xs text-gray-400 mb-2">Showing {filteredWorks.length} of {works.length} works</p>
      {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
      <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="bg-navy text-white text-left"><th className="p-3">Work ID / Title</th><th className="p-3">Category</th><th className="p-3">State</th><th className="p-3">Allocation</th><th className="p-3">Progress</th><th className="p-3">Status</th><th className="p-3">Risk</th></tr></thead>
          <tbody>
            {filteredWorks.map((work, index) => {
              const progress = progressFor(work.status);
              return <tr key={work.work_id} onClick={() => navigate(`/work/${work.work_id}`)} className={`cursor-pointer hover:bg-blue-50 ${index % 2 === 0 ? "bg-white" : "bg-gray-50"}`}>
                <td className="p-3"><p className="font-semibold text-navy">{work.title}</p><p className="text-xs text-gray-400">{work.work_id}</p></td>
                <td className="p-3">{work.category}</td><td className="p-3">{work.state}</td><td className="p-3">₹{(work.allocation_amount / 100000).toFixed(1)}L</td>
                <td className="p-3"><div className="w-24 bg-gray-200 rounded-full h-2 mb-1"><div className="h-2 rounded-full bg-green-400" style={{ width: `${progress}%` }} /></div><span className="text-xs text-gray-500">{progress}%</span></td>
                <td className="p-3"><span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[work.status] || "bg-gray-100 text-gray-600"}`}>{work.status}</span></td><td className="p-3">{work.risk_level || "Not assessed"}</td>
              </tr>;
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default WorksRegistry;

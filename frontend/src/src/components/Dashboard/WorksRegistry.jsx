import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { mockWorks, statusColors } from "../../utils/mockData";

function WorksRegistry() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const navigate = useNavigate();

  const filters = ["All", "Completed", "In Progress", "Delayed", "Stalled"];

  const filteredWorks = mockWorks.filter((work) => {
    const matchesSearch =
      work.title.toLowerCase().includes(search.toLowerCase()) ||
      work.id.toLowerCase().includes(search.toLowerCase()) ||
      work.district.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === "All" || work.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          type="text"
          placeholder="Search Works, ID, District..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm flex-1"
        />
        <div className="flex gap-2 flex-wrap">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-2 rounded text-sm ${
                filter === f
                  ? "bg-navy text-white"
                  : "bg-white border border-gray-300 text-gray-600"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <p className="text-xs text-gray-400 mb-2">
        Showing {filteredWorks.length} of {mockWorks.length} works — click a row for details
      </p>

      <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-navy text-white text-left">
              <th className="p-3">Work ID / Title</th>
              <th className="p-3">Category</th>
              <th className="p-3">District</th>
              <th className="p-3">Sanctioned (₹)</th>
              <th className="p-3">Spent (₹)</th>
              <th className="p-3">Progress</th>
              <th className="p-3">Status</th>
              <th className="p-3">Geo-Tag</th>
              <th className="p-3">Flags</th>
            </tr>
          </thead>
          <tbody>
            {filteredWorks.map((work, idx) => (
              <tr
                key={work.id}
                onClick={() => navigate(`/work/${work.id}`)}
                className={`cursor-pointer hover:bg-blue-50 ${
                  idx % 2 === 0 ? "bg-white" : "bg-gray-50"
                }`}
              >
                <td className="p-3">
                  <p className="font-semibold text-navy">{work.title}</p>
                  <p className="text-xs text-gray-400">
                    {work.id} · {work.agency}
                  </p>
                </td>
                <td className="p-3">{work.category}</td>
                <td className="p-3">{work.district}</td>
                <td className="p-3">
                  ₹{(work.sanctioned / 100000).toFixed(1)}L
                </td>
                <td className="p-3">₹{(work.spent / 100000).toFixed(1)}L</td>
                <td className="p-3">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mb-1">
                    <div
                      className={`h-2 rounded-full ${
                        work.status === "Stalled"
                          ? "bg-red-400"
                          : work.status === "Delayed"
                          ? "bg-orange-400"
                          : "bg-green-400"
                      }`}
                      style={{ width: `${work.progress}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-500">
                    {work.progress}%{" "}
                    {work.overdueDays > 0 && `· ${work.overdueDays}d overdue`}
                  </span>
                </td>
                <td className="p-3">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${statusColors[work.status]}`}
                  >
                    {work.status}
                  </span>
                </td>
                <td className="p-3">{work.geoTag ? "✅" : "❌"}</td>
                <td className="p-3">
                  {work.flags.map((flag) => (
                    <span
                      key={flag}
                      className="inline-block bg-red-50 text-red-600 text-xs px-2 py-1 rounded mr-1 mb-1"
                    >
                      {flag}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default WorksRegistry;
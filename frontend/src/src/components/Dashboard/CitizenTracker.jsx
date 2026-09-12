import { useState } from "react";
import { mockWorks, statusColors } from "../../utils/mockData";

function CitizenTracker() {
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("search");

  const filteredWorks = mockWorks.filter(
    (work) =>
      work.title.toLowerCase().includes(search.toLowerCase()) ||
      work.district.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      {/* Hero Banner */}
      <div className="bg-navy text-white rounded-lg p-6 mb-6 flex justify-between items-start">
        <div>
          <span className="bg-accent text-white text-xs px-2 py-1 rounded mb-2 inline-block">
            Citizen Transparency Portal
          </span>
          <h2 className="text-xl font-bold mb-1">
            Track Development Works in Your Area
          </h2>
          <p className="text-sm text-ice max-w-md">
            Every rupee spent under MPLADS is publicly accountable. Search,
            verify on ground, and report discrepancies — you are the last
            line of accountability.
          </p>
        </div>
        <div className="bg-white/10 rounded-lg px-4 py-3 text-center">
          <p className="text-2xl font-bold">{mockWorks.length}</p>
          <p className="text-xs text-ice">Works in your region</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-gray-200">
        {[
          { id: "search", label: "Search Works" },
          { id: "complaint", label: "File Complaint" },
          { id: "ai", label: "Ask AI Assistant" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              activeTab === tab.id
                ? "border-navy text-navy"
                : "border-transparent text-gray-400"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search Works Tab */}
      {activeTab === "search" && (
        <div>
          <input
            type="text"
            placeholder="Search by work name, village, or district..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4"
          />
          <div className="space-y-3">
            {filteredWorks.map((work) => (
              <div
                key={work.id}
                className="bg-white border border-gray-200 rounded-lg p-4 flex justify-between items-center"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400">{work.id}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${statusColors[work.status]}`}
                    >
                      {work.status}
                    </span>
                    {work.geoTag && (
                      <span className="text-xs text-green-600">
                        📍 Geo-Verified
                      </span>
                    )}
                  </div>
                  <p className="font-semibold text-navy text-sm">
                    {work.title}
                  </p>
                  <p className="text-xs text-gray-400">
                    {work.district} · {work.category} · Agency: {work.agency}
                  </p>
                  {work.flags.length > 0 && (
                    <p className="text-xs text-red-500 mt-1">
                      ⚠ {work.flags.join(", ")}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-navy">
                    ₹{(work.sanctioned / 100000).toFixed(1)}L
                  </p>
                  <p className="text-xs text-gray-400">sanctioned</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {work.progress}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File Complaint Tab */}
      {activeTab === "complaint" && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-400 text-sm">
          Select a work from "Search Works" first, then file a complaint
          against it — this connects to the Grievance module.
        </div>
      )}

      {/* AI Assistant Tab */}
      {activeTab === "ai" && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-400 text-sm">
          Citizen AI Assistant — stretch goal, built by AI/ML teammate.
        </div>
      )}
    </div>
  );
}

export default CitizenTracker;
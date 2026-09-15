import { useState } from "react";
import { mockFundEligibility } from "../../utils/mockData";

function FundReleaseGate() {
  const [works, setWorks] = useState(mockFundEligibility);
  const [selectedId, setSelectedId] = useState(works[0].workId);

  const selected = works.find((w) => w.workId === selectedId);

  const handleUploadProof = () => {
    // Simulate verification proof arriving — flips eligibility live for demo
    setWorks((prev) =>
      prev.map((w) =>
        w.workId === selectedId
          ? { ...w, eligible: true, verifiedCompletion: 100, blockingReasons: [] }
          : w
      )
    );
  };

  return (
    <div>
      <div className="bg-navy text-white rounded-lg p-5 mb-6">
        <p className="text-xs uppercase tracking-wide text-ice mb-1">
          Milestone-Gated Fund Release Engine
        </p>
        <p className="text-sm">
          The next installment cannot release until independently verified
          proof confirms the previous tranche was genuinely utilized.
        </p>
      </div>

      {/* Work selector */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {works.map((w) => (
          <button
            key={w.workId}
            onClick={() => setSelectedId(w.workId)}
            className={`px-3 py-2 rounded text-sm border ${
              selectedId === w.workId
                ? "bg-navy text-white border-navy"
                : "bg-white text-gray-600 border-gray-300"
            }`}
          >
            {w.workId}
          </button>
        ))}
      </div>

      {/* Eligibility Card */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-semibold text-navy">{selected.title}</h3>
            <p className="text-xs text-gray-400">{selected.workId}</p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              selected.eligible
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {selected.eligible ? "✅ Eligible" : "🚫 Blocked"}
          </span>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Verified Utilization</span>
            <span>
              {selected.verifiedCompletion}% / {selected.requiredPercent}% required
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${
                selected.eligible ? "bg-green-500" : "bg-orange-400"
              }`}
              style={{ width: `${Math.min(selected.verifiedCompletion, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Blocking reasons */}
        {!selected.eligible && (
          <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
            <p className="text-sm font-semibold text-red-700 mb-2">
              Blocking Reasons:
            </p>
            <ul className="text-sm text-red-600 list-disc list-inside space-y-1">
              {selected.blockingReasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </div>
        )}

        {selected.eligible && (
          <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
            <p className="text-sm text-green-700">
              All verification criteria met. Fund release approved and
              digitally signed.
            </p>
          </div>
        )}

        {/* Action button */}
        {!selected.eligible ? (
          <button
            onClick={handleUploadProof}
            className="bg-accent text-white px-4 py-2 rounded text-sm font-semibold hover:opacity-90"
          >
            Upload Verified Proof (Simulate)
          </button>
        ) : (
          <button
            disabled
            className="bg-gray-200 text-gray-400 px-4 py-2 rounded text-sm font-semibold cursor-not-allowed"
          >
            Fund Released ✓
          </button>
        )}
      </div>
    </div>
  );
}

export default FundReleaseGate;
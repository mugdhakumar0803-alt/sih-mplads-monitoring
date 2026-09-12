import { mockCompliance } from "../../utils/mockData";

function ComplianceBar({ label, current, required }) {
  const onTrack = current >= required;
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <p className="text-sm font-semibold text-navy">{label}</p>
        <span
          className={`text-xs font-semibold px-2 py-1 rounded ${
            onTrack ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          }`}
        >
          {onTrack ? "On Track" : "Below Threshold"}
        </span>
      </div>
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{current}% allocated</span>
        <span>{required}% required</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full ${onTrack ? "bg-green-500" : "bg-red-400"}`}
          style={{ width: `${Math.min((current / required) * 100, 100)}%` }}
        ></div>
      </div>
    </div>
  );
}

function ComplianceTracker() {
  const c = mockCompliance;

  return (
    <div>
      <div className="bg-navy text-white rounded-lg p-5 mb-6">
        <p className="text-xs uppercase tracking-wide text-ice mb-1">
          Statutory Compliance Rule Engine
        </p>
        <p className="text-sm">
          Deterministic checks against MPLADS statutory thresholds — SC/ST
          allocation and national priority area spending.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <ComplianceBar
          label="SC Area Allocation"
          current={c.scAllocationPercent}
          required={c.scRequiredPercent}
        />
        <ComplianceBar
          label="ST Area Allocation"
          current={c.stAllocationPercent}
          required={c.stRequiredPercent}
        />
        <ComplianceBar
          label="National Priority Area"
          current={c.priorityAreaPercent}
          required={c.priorityAreaRequiredPercent}
        />
      </div>
    </div>
  );
}

export default ComplianceTracker;
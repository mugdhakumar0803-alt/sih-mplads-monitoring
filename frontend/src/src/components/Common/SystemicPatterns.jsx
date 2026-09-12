import { mockSystemicPatterns } from "../../utils/mockData";

const severityStyles = {
  high: "bg-red-50 border-red-200 text-red-700",
  medium: "bg-orange-50 border-orange-200 text-orange-700",
  low: "bg-green-50 border-green-200 text-green-700",
};

function SystemicPatterns() {
  return (
    <div>
      <div className="bg-navy text-white rounded-lg p-5 mb-6">
        <p className="text-xs uppercase tracking-wide text-ice mb-1">
          Systemic Pattern Flagging
        </p>
        <p className="text-sm">
          A single escalated case may be a one-off. Repeated escalations from
          the same authority signal a systemic issue worth Ministry attention.
        </p>
      </div>

      <div className="space-y-3">
        {mockSystemicPatterns.map((p) => (
          <div
            key={p.district}
            className={`border rounded-lg p-4 flex justify-between items-center ${severityStyles[p.severity]}`}
          >
            <div>
              <p className="font-semibold">{p.district}</p>
              <p className="text-xs opacity-75">{p.period}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">{p.escalatedCases}</p>
              <p className="text-xs">cases escalated to Ministry</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SystemicPatterns;
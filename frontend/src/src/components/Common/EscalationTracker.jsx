import { mockEscalation } from "../../utils/mockData";

function EscalationTracker() {
  const e = mockEscalation;

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Left: Escalation timeline */}
      <div className="md:col-span-2">
        <div className="bg-white border border-gray-200 rounded-lg p-5 mb-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="bg-red-100 text-red-700 text-xs font-semibold px-2 py-1 rounded">
                ACTIVE ESCALATION
              </span>
              <h3 className="font-semibold text-navy mt-2">{e.workTitle}</h3>
              <p className="text-xs text-gray-400">
                {e.workId} · {e.district}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-red-600">
                {e.overdueDays}
              </p>
              <p className="text-xs text-gray-400">days overdue</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
            <div
              className="h-2 rounded-full bg-red-400"
              style={{ width: `${e.progress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500">
            {e.progress}% — {e.status}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <p className="text-sm font-semibold text-navy mb-4">
            Escalation Timeline
          </p>
          <div className="space-y-4">
            {e.timeline.map((item, idx) => (
              <div key={idx} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-2.5 h-2.5 rounded-full bg-navy mt-1"></div>
                  {idx !== e.timeline.length - 1 && (
                    <div className="w-px flex-1 bg-gray-200 mt-1"></div>
                  )}
                </div>
                <div className="flex-1 pb-2">
                  <div className="flex justify-between">
                    <p className="text-sm text-gray-700">{item.event}</p>
                    <span className="text-xs text-gray-400">{item.date}</span>
                  </div>
                  <p className="text-xs text-gray-400">{item.by}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right: Force-majeure filter */}
      <div>
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <p className="text-sm font-semibold text-navy mb-2">
            Force Majeure Filter
          </p>
          <p className="text-xs text-gray-500 mb-4">
            System cross-references NDMA disaster declarations against delay
            windows. Officials are not penalized for calamity-caused delays.
          </p>
          <div className="space-y-3">
            {e.forceMajeure.map((f) => (
              <div
                key={f.district}
                className={`border rounded p-3 ${
                  f.status === "exempted"
                    ? "border-green-200 bg-green-50"
                    : "border-gray-200 bg-gray-50"
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-semibold text-navy">
                    {f.district}
                  </span>
                  {f.status === "exempted" ? (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                      ✓ Exempted
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-200 text-gray-500 px-2 py-0.5 rounded">
                      N/A
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500">{f.reason}</p>
                {f.worksExempted && (
                  <p className="text-xs text-green-600 mt-1">
                    ✓ {f.worksExempted} works exempted from SLA penalty
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EscalationTracker;
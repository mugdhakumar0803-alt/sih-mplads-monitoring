import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client";

function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/alerts").then((result) => setAlerts(result.alerts || [])).catch((requestError) => setError(requestError.message));
  }, []);

  return <div className="bg-white border border-gray-200 rounded-lg p-5"><p className="font-semibold text-navy text-sm mb-3">Project Alerts</p>{error && <p className="text-sm text-red-600">{error}</p>}{!error && alerts.length === 0 && <p className="text-sm text-gray-500">No alerts for the projects in your scope.</p>}{alerts.map((alert) => <div key={alert.alert_id} className="border-b last:border-b-0 py-3"><div className="flex justify-between"><p className="text-sm font-semibold text-navy">{alert.type}</p><span className="text-xs text-red-600">{alert.severity}</span></div><p className="text-xs text-gray-600 mt-1">{alert.message}</p><p className="text-xs text-gray-400 mt-1">{alert.work_id || "System"}</p></div>)}</div>;
}

export default AlertsPanel;

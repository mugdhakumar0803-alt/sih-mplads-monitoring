import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getProgressVsUtilization } from "../../services/analyticsApi";

export default function ProgressVsUtilizationChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getProgressVsUtilization().then(setData);
  }, []);

  return (
    <div className="chart-card">
      <h3>Work Progress vs Fund Utilization</h3>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <XAxis dataKey="month" />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="physical_progress_pct" stroke="#2563eb" name="Physical Progress %" />
          <Line type="monotone" dataKey="financial_utilization_pct" stroke="#dc2626" name="Financial Utilization %" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
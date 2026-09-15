import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getFundUtilization } from "../../services/analyticsApi";

export default function FundUtilizationChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getFundUtilization().then(setData);
  }, []);

  return (
    <div className="chart-card">
      <h3>Fund Utilization by Work</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <XAxis dataKey="work" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="allocated" stackId="funds" fill="#2563eb" name="Allocated" />
          <Bar dataKey="released" stackId="funds" fill="#16a34a" name="Released" />
          <Bar dataKey="utilized" stackId="funds" fill="#f59e0b" name="Utilized" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

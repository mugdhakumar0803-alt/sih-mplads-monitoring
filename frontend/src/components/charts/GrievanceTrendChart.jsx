import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getGrievanceTrend } from "../../services/analyticsApi";

export default function GrievanceTrendChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getGrievanceTrend().then(setData);
  }, []);

  return (
    <div className="chart-card">
      <h3>Grievance Resolution Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="filed" stroke="#dc2626" name="Filed" />
          <Line type="monotone" dataKey="resolved" stroke="#16a34a" name="Resolved" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
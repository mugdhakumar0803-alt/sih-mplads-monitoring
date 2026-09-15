import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getRiskDistribution } from "../../services/analyticsApi";

const COLORS = { Low: "#16a34a", Medium: "#facc15", High: "#dc2626" };

export default function RiskDistributionChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getRiskDistribution().then(setData);
  }, []);

  return (
    <div className="chart-card">
      <h3>Risk Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="level" innerRadius={60} outerRadius={100}>
            {data.map((entry, i) => (
              <Cell key={i} fill={COLORS[entry.level] || "#999"} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
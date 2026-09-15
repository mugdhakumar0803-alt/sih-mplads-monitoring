import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getConstituencyRanking } from "../../services/analyticsApi";

export default function ConstituencyRankingChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getConstituencyRanking("completion").then(setData);
  }, []);

  return (
    <div className="chart-card">
      <h3>Constituency Performance Ranking</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
          <XAxis type="number" domain={[0, 100]} />
          <YAxis type="category" dataKey="constituency" width={100} />
          <Tooltip />
          <Bar dataKey="score" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
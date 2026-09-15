import FundUtilizationChart from "../components/charts/FundUtilizationChart";
import ProgressVsUtilizationChart from "../components/charts/ProgressVsUtilizationChart";
import RiskDistributionChart from "../components/charts/RiskDistributionChart";
import GrievanceTrendChart from "../components/charts/GrievanceTrendChart";
import ConstituencyRankingChart from "../components/charts/ConstituencyRankingChart";

export default function AnalyticsDashboard() {
  return (
    <div className="analytics-dashboard">
      <h2>PanchSetu — Monitoring & Insights</h2>

      <div className="grid grid-2">
        <FundUtilizationChart />
        <ProgressVsUtilizationChart />
      </div>

      <div className="grid grid-2">
        <RiskDistributionChart />
        <ConstituencyRankingChart />
      </div>

      <div className="grid grid-1">
        <GrievanceTrendChart />
      </div>
    </div>
  );
}
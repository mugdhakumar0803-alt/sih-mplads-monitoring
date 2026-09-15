import { useState } from "react";
import DashboardLayout from "../components/Common/DashboardLayout";
import OverviewStats from "../components/Dashboard/OverviewStats";
import WorksRegistry from "../components/Dashboard/WorksRegistry";
import FundReleaseGate from "../components/FundRelease/FundReleaseGate";
import GrievancePanel from "../components/Grievance/GrievancePanel";
import ComplianceTracker from "../components/Compliance/ComplianceTracker";
import EscalationTracker from "../components/Common/EscalationTracker";

function MPDashboard() {
  const [activeTab, setActiveTab] = useState("Overview");

  const navItems = [
    { label: "Overview" },
    { label: "Works Registry" },
    { label: "Fund Release" },
    { label: "Grievances & SLA" },
    { label: "Escalation" },
    { label: "Compliance" },
  ];

  return (
    <DashboardLayout
      title="MP Dashboard"
      navItems={navItems.map((n) => ({
        ...n,
        onClick: () => setActiveTab(n.label),
        active: activeTab === n.label,
      }))}
    >
      {activeTab === "Overview" && <OverviewStats />}
      {activeTab === "Works Registry" && <WorksRegistry />}
      {activeTab === "Fund Release" && <FundReleaseGate />}
      {activeTab === "Grievances & SLA" && <GrievancePanel />}
      {activeTab === "Escalation" && <EscalationTracker />}
      {activeTab === "Compliance" && <ComplianceTracker />}
    </DashboardLayout>
  );
}

export default MPDashboard;
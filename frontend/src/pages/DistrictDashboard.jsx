import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import WorksRegistry from "../components/Dashboard/WorksRegistry";
import GrievancePanel from "../components/Grievance/GrievancePanel";
import EscalationTracker from "../components/Common/EscalationTracker";

function DistrictDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("Overview");

  const navItems = [
    { label: "Overview" },
    { label: "Works Registry" },
    { label: "Grievances & SLA" },
    { label: "Escalation" },
  ];

  return (
    <DashboardLayout
      title="District Authority Dashboard"
      navItems={navItems.map((n) => ({
        ...n,
        onClick: () => setActiveTab(n.label),
        active: activeTab === n.label,
      }))}
    >
      {activeTab === "Overview" && (
        <p className="text-gray-600">
          Welcome, {user?.name}. Your district's works overview here.
        </p>
      )}
      {activeTab === "Works Registry" && <WorksRegistry />}
      {activeTab === "Grievances & SLA" && <GrievancePanel />}
      {activeTab === "Escalation" && <EscalationTracker />}
    </DashboardLayout>
  );
}

export default DistrictDashboard;
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import WorksRegistry from "../components/Dashboard/WorksRegistry";
import SystemicPatterns from "../components/Common/SystemicPatterns";
import EscalationTracker from "../components/Common/EscalationTracker";

function MinistryDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("National Overview");

  const navItems = [
    { label: "National Overview" },
    { label: "Systemic Patterns" },
    { label: "Escalated Cases" },
  ];

  return (
    <DashboardLayout
      title="Ministry Dashboard"
      navItems={navItems.map((n) => ({
        ...n,
        onClick: () => setActiveTab(n.label),
        active: activeTab === n.label,
      }))}
    >
      {activeTab === "National Overview" && (
        <div>
          <p className="text-gray-600 mb-4">
            Welcome, {user?.name}. National overview of all works.
          </p>
          <WorksRegistry />
        </div>
      )}
      {activeTab === "Systemic Patterns" && <SystemicPatterns />}
      {activeTab === "Escalated Cases" && <EscalationTracker />}
    </DashboardLayout>
  );
}

export default MinistryDashboard;
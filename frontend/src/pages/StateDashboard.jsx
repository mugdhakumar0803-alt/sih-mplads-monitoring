import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import EscalationTracker from "../components/Common/EscalationTracker";
import ComplianceTracker from "../components/Compliance/ComplianceTracker";

function StateDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("Overview");

  const navItems = [
    { label: "Overview" },
    { label: "Escalations" },
    { label: "Compliance" },
  ];

  return (
    <DashboardLayout
      title="State Nodal Dashboard"
      navItems={navItems.map((n) => ({
        ...n,
        onClick: () => setActiveTab(n.label),
        active: activeTab === n.label,
      }))}
    >
      {activeTab === "Overview" && (
        <p className="text-gray-600">
          Welcome, {user?.name}. Your state's overview here.
        </p>
      )}
      {activeTab === "Escalations" && <EscalationTracker />}
      {activeTab === "Compliance" && <ComplianceTracker />}
    </DashboardLayout>
  );
}

export default StateDashboard;
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import OverviewStats from "../components/Dashboard/OverviewStats";
import EscalationTracker from "../components/Common/EscalationTracker";
import ComplianceTracker from "../components/Compliance/ComplianceTracker";
import ChatbotWidget from "../components/Chatbot/ChatbotWidget";

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
        <div>
          <p className="text-gray-600 mb-4">
            Welcome, {user?.name}. Your state's overview here.
          </p>
          <OverviewStats />
        </div>
      )}
      {activeTab === "Escalations" && <EscalationTracker />}
      {activeTab === "Compliance" && <ComplianceTracker />}
      <div className="mt-6"><ChatbotWidget /></div>
    </DashboardLayout>
  );
}

export default StateDashboard;
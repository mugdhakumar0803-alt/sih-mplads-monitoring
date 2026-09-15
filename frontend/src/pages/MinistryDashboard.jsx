import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import OverviewStats from "../components/Dashboard/OverviewStats";
import WorksRegistry from "../components/Dashboard/WorksRegistry";
import SystemicPatterns from "../components/Common/SystemicPatterns";
import EscalationTracker from "../components/Common/EscalationTracker";
import ChatbotWidget from "../components/Chatbot/ChatbotWidget";

function MinistryDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("National Overview");

  const navItems = [
    { label: "National Overview" },
    { label: "Systemic Patterns" },
    { label: "Escalated Cases" },
    { label: "Ask AI" },
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
          <OverviewStats />
          <div className="mt-6">
            <WorksRegistry />
          </div>
        </div>
      )}
      {activeTab === "Systemic Patterns" && <SystemicPatterns />}
      {activeTab === "Escalated Cases" && <EscalationTracker />}
      {activeTab === "Ask AI" && <ChatbotWidget />}
    </DashboardLayout>
  );
}

export default MinistryDashboard;
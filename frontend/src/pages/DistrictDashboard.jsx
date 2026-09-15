import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";
import OverviewStats from "../components/Dashboard/OverviewStats";
import WorksRegistry from "../components/Dashboard/WorksRegistry";
import GrievancePanel from "../components/Grievance/GrievancePanel";
import EscalationTracker from "../components/Common/EscalationTracker";
import ChatbotWidget from "../components/Chatbot/ChatbotWidget";

function DistrictDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("Overview");

  const navItems = [
    { label: "Overview" },
    { label: "Works Registry" },
    { label: "Grievances & SLA" },
    { label: "Escalation" },
    { label: "Ask AI" },
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
        <div>
          <p className="text-gray-600 mb-4">
            Welcome, {user?.name}. Your district's works overview here.
          </p>
          <OverviewStats />
        </div>
      )}
      {activeTab === "Works Registry" && <WorksRegistry />}
      {activeTab === "Grievances & SLA" && <GrievancePanel />}
      {activeTab === "Escalation" && <EscalationTracker />}
      {activeTab === "Ask AI" && <ChatbotWidget />}
    </DashboardLayout>
  );
}

export default DistrictDashboard;
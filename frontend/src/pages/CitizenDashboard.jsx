import { useState } from "react";
import DashboardLayout from "../components/Common/DashboardLayout";
import CitizenTracker from "../components/Dashboard/CitizenTracker";
import GrievancePanel from "../components/Grievance/GrievancePanel";

function CitizenDashboard() {
  const [activeTab, setActiveTab] = useState("Track Works");

  const navItems = [
    { label: "Track Works" },
    { label: "File Grievance" },
  ];

  return (
    <DashboardLayout
      title="Citizen Portal"
      navItems={navItems.map((n) => ({
        ...n,
        onClick: () => setActiveTab(n.label),
        active: activeTab === n.label,
      }))}
    >
      {activeTab === "Track Works" && <CitizenTracker />}
      {activeTab === "File Grievance" && <GrievancePanel />}
    </DashboardLayout>
  );
}

export default CitizenDashboard;
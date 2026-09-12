import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";

function MinistryDashboard() {
  const { user } = useAuth();

  const navItems = [
    { label: "National Overview" },
    { label: "Systemic Patterns" },
    { label: "Escalated Cases" },
  ];

  return (
    <DashboardLayout title="Ministry Dashboard" navItems={navItems}>
      <p className="text-gray-600">
        Welcome, {user?.name}. National overview here.
      </p>
    </DashboardLayout>
  );
}

export default MinistryDashboard;
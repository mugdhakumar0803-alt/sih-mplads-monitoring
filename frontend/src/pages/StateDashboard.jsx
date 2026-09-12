import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";

function StateDashboard() {
  const { user } = useAuth();

  const navItems = [
    { label: "Overview" },
    { label: "Escalations" },
    { label: "Compliance" },
  ];

  return (
    <DashboardLayout title="State Nodal Dashboard" navItems={navItems}>
      <p className="text-gray-600">
        Welcome, {user?.name}. Your state's overview here.
      </p>
    </DashboardLayout>
  );
}

export default StateDashboard;
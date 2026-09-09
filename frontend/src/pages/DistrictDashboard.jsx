import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../components/Common/DashboardLayout";

function DistrictDashboard() {
  const { user } = useAuth();

  const navItems = [
    { label: "Overview" },
    { label: "Works Registry" },
    { label: "Grievances & SLA" },
    { label: "Photo Verification" },
  ];

  return (
    <DashboardLayout title="District Authority Dashboard" navItems={navItems}>
      <p className="text-gray-600">
        Welcome, {user?.name}. Your district's works here.
      </p>
    </DashboardLayout>
  );
}

export default DistrictDashboard;
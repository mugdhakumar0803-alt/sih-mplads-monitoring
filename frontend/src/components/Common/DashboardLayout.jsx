
import { useAuth } from "../../context/AuthContext";
import BrandLogo from "./BrandLogo";

const roleLabels = {
  citizen: "Citizen",
  mp: "Member of Parliament",
  district: "District Authority",
  state: "State Nodal Authority",
  ministry: "Ministry",
};

function DashboardLayout({ title, navItems = [], children }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-60 bg-navy text-white flex flex-col">
        <div className="p-5 border-b border-white/10">
          <BrandLogo compact dark className="items-start" />
          <p className="text-xs text-ice mt-1">{roleLabels[user?.role]}</p>
        </div>
        <nav className="flex-1 p-3 flex flex-col gap-1">
          {navItems.map((item) => (
            <button
              key={item.label}
              onClick={item.onClick}
              className={`text-left px-3 py-2 rounded text-sm transition ${
                item.active ? "bg-white/15 font-semibold" : "hover:bg-white/10"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-white/10">
          <p className="text-xs text-ice mb-2 truncate">{user?.email}</p>
          <button
            onClick={logout}
            className="text-sm text-red-300 hover:text-red-200"
          >
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <h1 className="text-2xl font-bold text-navy mb-6">{title}</h1>
        {children}
      </main>
    </div>
  );
}

export default DashboardLayout;
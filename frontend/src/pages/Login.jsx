import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roles = [
  { id: "citizen", label: "Citizen", icon: "👤", path: "/citizen" },
  { id: "mp", label: "Member of Parliament", icon: "🏛️", path: "/mp" },
  { id: "district", label: "District Authority", icon: "📍", path: "/district" },
  { id: "state", label: "State Nodal Authority", icon: "🗺️", path: "/state" },
  { id: "ministry", label: "Ministry", icon: "🏢", path: "/ministry" },
];

function Login() {
  const [selectedRole, setSelectedRole] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) return;
    login(selectedRole, email);
    const role = roles.find((r) => r.id === selectedRole);
    navigate(role.path);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-navy">eSAMEEKSHA</h1>
        <p className="text-gray-500 text-sm mt-1">
          MPLADS Monitoring & Accountability Portal
        </p>
      </div>

      {!selectedRole && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-2xl w-full">
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => setSelectedRole(role.id)}
              className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center gap-2 hover:border-navy hover:shadow-md transition"
            >
              <span className="text-3xl">{role.icon}</span>
              <span className="text-sm font-semibold text-navy text-center">
                {role.label}
              </span>
            </button>
          ))}
        </div>
      )}

      {selectedRole && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 w-full max-w-sm">
          <button
            onClick={() => setSelectedRole(null)}
            className="text-sm text-gray-400 mb-4"
          >
            ← Back
          </button>
          <h2 className="text-lg font-bold text-navy mb-4">
            Login as {roles.find((r) => r.id === selectedRole)?.label}
          </h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <button
              type="submit"
              className="bg-navy text-white rounded py-2 text-sm font-semibold mt-2 hover:opacity-90"
            >
              Login
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default Login;
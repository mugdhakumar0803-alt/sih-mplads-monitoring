import { useState } from "react";
import { useNavigate } from "react-router-dom";
import BrandLogo from "../components/Common/BrandLogo";
import { useAuth } from "../context/AuthContext";

const roles = [
  { id: "citizen", label: "Citizen", icon: "👤", path: "/citizen" },
  { id: "mp", label: "Member of Parliament", icon: "🏛️", path: "/mp" },
  { id: "district_official", label: "District Authority", icon: "📍", path: "/district" },
  { id: "state_official", label: "State Nodal Authority", icon: "🗺️", path: "/state" },
  { id: "ministry", label: "Ministry", icon: "🏢", path: "/ministry" },
];

function Login() {
  const [selectedRole, setSelectedRole] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!username.trim() || !password) {
      setError("Enter your username and password.");
      return;
    }
    try {
      const profile = await login(username, password);
      const role = roles.find((r) => r.id === profile.role);
      if (!role) throw new Error("This account has no dashboard configured");
      navigate(role.path);
    } catch (loginError) {
      setError(loginError.message || "Login failed");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="text-center mb-10">
        <BrandLogo />
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
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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
          {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
        </div>
      )}
    </div>
  );
}

export default Login;
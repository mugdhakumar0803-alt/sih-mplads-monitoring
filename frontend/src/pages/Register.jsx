import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import panchsetuLogo from "../assets/panchsetu-logo.png";

const roles = [
  { id: "citizen", label: "Citizen", icon: "👤", path: "/citizen" },
  { id: "mp", label: "Member of Parliament", icon: "🏛️", path: "/mp" },
  { id: "district", label: "District Authority", icon: "📍", path: "/district" },
  { id: "state", label: "State Nodal Authority", icon: "🗺️", path: "/state" },
  { id: "ministry", label: "Ministry", icon: "🏢", path: "/ministry" },
];

// Roles that require an admin to approve them before they can log in.
// Backend mirrors this — see auth/routes.py.
const REQUIRES_APPROVAL = ["mp", "district", "state", "ministry"];

function Register() {
  const [selectedRole, setSelectedRole] = useState(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState("");
  const [district, setDistrict] = useState("");
  const [constituency, setConstituency] = useState("");
  const [house, setHouse] = useState("lok_sabha");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submittedPending, setSubmittedPending] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const needsState = ["mp", "district", "state"].includes(selectedRole);
  const needsConstituency = selectedRole === "mp";
  const needsHouse = selectedRole === "mp";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError("Enter your name, email, and password.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      const backendRole = selectedRole === "district" ? "district_official" : selectedRole === "state" ? "state_official" : selectedRole;
      const registration = await register({
        username: email,
        email,
        password,
        role: backendRole,
        state: state || undefined,
        district_id: district || undefined,
        constituency: constituency || undefined,
        house: selectedRole === "mp" ? house : undefined,
      });
      if (registration.approval_status === "pending") {
        setSubmittedPending(true);
      } else {
        const role = roles.find((r) => r.id === selectedRole);
        navigate(role.path);
      }
    } catch (err) {
      setError(err.message || "Registration failed — please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <img src={panchsetuLogo} alt="PANCHSETU" className="w-24 mb-4" />
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-navy">Create an Account</h1>
        <p className="text-gray-500 text-sm mt-1">
          Register for PANCHSETU access
        </p>
      </div>

      {submittedPending && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 w-full max-w-sm text-center">
          <p className="text-lg font-bold text-navy mb-2">Account created</p>
          <p className="text-sm text-gray-500">
            Your account is awaiting approval from an administrator. You'll
            be able to log in once it's approved.
          </p>
          <Link to="/login" className="text-navy font-semibold text-sm mt-4 inline-block">
            Back to login
          </Link>
        </div>
      )}

      {!submittedPending && !selectedRole && (
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

      {!submittedPending && selectedRole && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 w-full max-w-sm">
          <button
            onClick={() => setSelectedRole(null)}
            className="text-sm text-gray-400 mb-4"
          >
            ← Back
          </button>
          <h2 className="text-lg font-bold text-navy mb-4">
            Register as {roles.find((r) => r.id === selectedRole)?.label}
          </h2>

          {REQUIRES_APPROVAL.includes(selectedRole) && (
            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 mb-3">
              This role needs approval from an administrator before you can log in.
            </p>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            />
            {(selectedRole === "mp" || selectedRole === "district" || selectedRole === "state" || selectedRole === "citizen") && (
              <input
                type="text"
                placeholder="State"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
            )}
            {selectedRole === "district" && (
              <input
                type="text"
                placeholder="District"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
            )}
            {selectedRole === "mp" && (
              <>
                <select value={house} onChange={(e) => setHouse(e.target.value)} className="border border-gray-300 rounded px-3 py-2 text-sm">
                  <option value="lok_sabha">Lok Sabha</option>
                  <option value="rajya_sabha">Rajya Sabha</option>
                </select>
                <input
                  type="text"
                  placeholder="Constituency"
                  value={constituency}
                  onChange={(e) => setConstituency(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </>
            )}
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

            {needsHouse && (
              <select
                value={house}
                onChange={(e) => setHouse(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="lok_sabha">Lok Sabha</option>
                <option value="rajya_sabha">Rajya Sabha</option>
              </select>
            )}

            {needsState && (
              <input
                type="text"
                placeholder="State"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
            )}

            {needsConstituency && (
              <input
                type="text"
                placeholder="Constituency"
                value={constituency}
                onChange={(e) => setConstituency(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm"
              />
            )}

            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="bg-navy text-white rounded py-2 text-sm font-semibold mt-2 hover:opacity-90 disabled:opacity-50"
            >
              {submitting ? "Creating account..." : "Create Account"}
            </button>
          </form>
        </div>
      )}

      <p className="text-sm text-gray-500 mt-6">
        Already have an account?{" "}
        <Link to="/login" className="text-navy font-semibold">
          Login here
        </Link>
      </p>
    </div>
  );
}

export default Register;

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/Common/ProtectedRoute";
import Login from "./pages/Login";
import CitizenDashboard from "./pages/CitizenDashboard";
import MPDashboard from "./pages/MPDashboard";
import DistrictDashboard from "./pages/DistrictDashboard";
import StateDashboard from "./pages/StateDashboard";
import MinistryDashboard from "./pages/MinistryDashboard";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route
            path="/citizen"
            element={
              <ProtectedRoute allowedRole="citizen">
                <CitizenDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mp"
            element={
              <ProtectedRoute allowedRole="mp">
                <MPDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/district"
            element={
              <ProtectedRoute allowedRole="district">
                <DistrictDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/state"
            element={
              <ProtectedRoute allowedRole="state">
                <StateDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ministry"
            element={
              <ProtectedRoute allowedRole="ministry">
                <MinistryDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
import { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, loginRequest, registerRequest } from "../api/client";

/* eslint-disable react-refresh/only-export-components */

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem("mplads_token")));

  useEffect(() => {
    if (!localStorage.getItem("mplads_token")) {
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem("mplads_token"))
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const token = await loginRequest(username, password);
    localStorage.setItem("mplads_token", token.access_token);
    const profile = await getCurrentUser();
    setUser(profile);
    return profile;
  };

  const ROLES_REQUIRING_APPROVAL = ["mp", "district", "state", "ministry"];

  // Registers with the real backend. Citizens are auto-approved and get
  // logged straight in. MP/District/State/Ministry accounts are created
  // as "pending" — the backend rejects login for those until an admin
  // approves them (see approve_user.py) — so we don't attempt to log
  // them in immediately.
  const register = async (role, name, email, password, extra = {}) => {
    await registerRequest({
      username: email,   // backend expects `username` — using email keeps it unique and simple
      email,
      password,
      role,
      state: extra.state,
      constituency: extra.constituency,
      house: extra.house,
    });

    if (ROLES_REQUIRING_APPROVAL.includes(role)) {
      return null;
    }
    return login(email, password);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("mplads_token");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

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

  const register = async (userData) => {
    const registration = await registerRequest({
      username: userData.username || userData.email,
      ...userData,
    });
    if (registration.approval_status === "approved") {
      return login(userData.username || userData.email, userData.password);
    }
    return registration;
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

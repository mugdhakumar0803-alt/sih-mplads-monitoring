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

  // NEW — this didn't exist before, which is why Register.jsx crashed
  // silently on submit. Registers with the real backend, then logs the
  // user in immediately afterward so they land straight in the app.
  const register = async (role, name, email, password) => {
    await registerRequest({
      username: email,   // backend expects `username` — using email keeps it unique and simple
      email,
      password,
      role,
    });
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

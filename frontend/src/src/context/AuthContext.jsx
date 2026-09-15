import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = (role, email) => {
    const mockUser = { role, email, name: email.split("@")[0] };
    setUser(mockUser);
    localStorage.setItem("mplads_user", JSON.stringify(mockUser));
  };

  const register = (role, name, email) => {
    // Mock registration — in production this calls POST /auth/register
    const mockUser = { role, email, name };
    setUser(mockUser);
    localStorage.setItem("mplads_user", JSON.stringify(mockUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("mplads_user");
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
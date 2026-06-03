import { createContext, useContext, useState, useCallback } from "react";

/**
 * AuthContext — shared authentication state across the app.
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback((newToken, userData) => {
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * useAuth hook - manages authentication state (token & user).
 * Token and user are persisted to localStorage and shared via context.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

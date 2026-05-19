import { useState } from "react";
import Dashboard from "./pages/Dashboard";

/**
 * App root.
 *
 * Auth state lives here (per frontend_plan.md §4):
 *   - token  : JWT string or null (persisted to localStorage)
 *   - user   : UserOut object or null
 *
 * Currently routes only to <Dashboard>. Extend with a router if
 * additional pages (e.g. /history, /auth) are added.
 */
export default function App() {
  // Auth state — lazy initializer reads localStorage once on mount
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);
  const [user, setUser] = useState(null);

  function handleLogin(newToken, userData) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  return (
    <div style={{ backgroundColor: "var(--color-canvas)", color: "var(--color-text-primary)" }} className="min-h-screen font-body">
      <Dashboard
        token={token}
        user={user}
        onLogin={handleLogin}
        onLogout={handleLogout}
      />
    </div>
  );
}

import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { token, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/auth");
  };

  // Initials for avatar
  const initials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : "FN";

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        minHeight: "52px",
        background: "#fff",
        borderBottom: "0.5px solid var(--color-border)",
      }}
    >
      {/* Wordmark: Fin + accent "o" + va */}
      <Link
        to="/"
        className="font-display"
        style={{
          fontWeight: 700,
          fontSize: "23px",
          letterSpacing: "0.01em",
          color: "var(--color-text-primary)",
          textDecoration: "none",
        }}
      >
        Fin<span style={{ color: "var(--color-accent)" }}>o</span>va
      </Link>

      {/* Navigation links (only when logged in) */}
      {token && (
        <div style={{ display: "flex", alignItems: "center", gap: "24px", flex: 1, marginLeft: "48px" }}>
          <Link
            to="/dashboard"
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              textDecoration: "none",
            }}
            className="btn-ghost"
          >
            Dashboard
          </Link>
          <Link
            to="/analyze"
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              textDecoration: "none",
            }}
            className="btn-ghost"
          >
            Analyze
          </Link>
          <Link
            to="/history"
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              textDecoration: "none",
            }}
            className="btn-ghost"
          >
            History
          </Link>
          <Link
            to="/supported-routes"
            style={{
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              textDecoration: "none",
            }}
            className="btn-ghost"
          >
            Routes
          </Link>
        </div>
      )}

      {/* Auth area */}
      {token ? (
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            className="font-mono-custom"
            style={{ fontSize: "11px", color: "#9A9690" }}
          >
            {user?.email ?? ""}
          </span>
          {/* Avatar circle */}
          <button
            onClick={handleLogout}
            title="Sign out"
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              background: "var(--color-accent-light)",
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "'DM Mono', monospace",
              fontSize: "9px",
              color: "var(--color-accent)",
              fontWeight: 500,
            }}
          >
            {initials}
          </button>
        </div>
      ) : (
        <Link
          to="/auth"
          className="btn-ghost"
          style={{ fontSize: "12px", textDecoration: "none", color: "var(--color-text-secondary)" }}
        >
          Sign in
        </Link>
      )}
    </nav>
  );
}

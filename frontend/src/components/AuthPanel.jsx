import { useState } from "react";
import { login as apiLogin, register as apiRegister } from "../services/api";

/**
 * AuthPanel — Login / Register toggle
 *
 * Props:
 *   onLogin : (token: string, user: object) => void
 *
 * Shown when token is null. Toggles between LoginForm and RegisterForm.
 */
export default function AuthPanel({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        // api.js login() correctly sends OAuth2 form-encoded (username/password)
        const data = await apiLogin(email, password);
        const token = data.access_token;
        const user = data.user || { email };
        onLogin(token, user);
      } else {
        // Register then auto-login
        await apiRegister(email, password);
        const data = await apiLogin(email, password);
        const token = data.access_token;
        const user = data.user || { email };
        onLogin(token, user);
      }
    } catch (err) {
      setError(err.message ?? "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "calc(100vh - 200px)" }}>
      <div style={{ background: "#fff", border: "0.5px solid var(--color-border)", borderRadius: "var(--radius-xl)", padding: "36px 40px", maxWidth: "420px", width: "100%" }}>
        <p style={{ fontSize: "11px", color: "#A8A39C", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "8px" }}>Finova</p>
        <h1 className="text-heading-1" style={{ color: "var(--color-text-primary)", marginBottom: "24px" }}>
          {isLogin ? "Sign in" : "Create account"}
        </h1>

        {/* Error banner */}
        {error && (
          <div
            className="mb-4 p-3 rounded-md text-sm"
            style={{
              backgroundColor: "var(--color-error-bg)",
              border: "0.5px solid var(--color-error-border)",
              color: "var(--color-error-text)",
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label
              htmlFor="auth-email"
              className="text-label block mb-2"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Email
            </label>
            <input
              id="auth-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              placeholder="you@email.com"
              required
              style={{
                width: "100%",
                height: "40px",
                backgroundColor: "var(--color-surface)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-primary)",
              }}
              className="border rounded-md px-3 font-body focus:outline-none"
              onFocus={(e) => (e.target.style.borderColor = "var(--color-border-strong)")}
              onBlur={(e) => (e.target.style.borderColor = "var(--color-border)")}
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="auth-password"
              className="text-label block mb-2"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Password
            </label>
            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
              style={{
                width: "100%",
                height: "40px",
                backgroundColor: "var(--color-surface)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-primary)",
              }}
              className="border rounded-md px-3 font-body focus:outline-none"
              onFocus={(e) => (e.target.style.borderColor = "var(--color-border-strong)")}
              onBlur={(e) => (e.target.style.borderColor = "var(--color-border)")}
            />
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full mt-6"
            style={{
              backgroundColor: loading ? "rgba(28, 28, 26, 0.6)" : "var(--color-text-primary)",
              color: "var(--color-canvas)",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Processing..." : isLogin ? "Sign in" : "Create account"}
          </button>
        </form>

        {/* Toggle link */}
        <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
            }}
            className="btn-ghost"
            style={{ color: "var(--color-text-accent)" }}
          >
            {isLogin ? "Create one" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}

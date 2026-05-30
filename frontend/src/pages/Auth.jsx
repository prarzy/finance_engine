import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { login as apiLogin, register as apiRegister } from "../services/api";

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let token, userData;
      
      if (isLogin) {
        const data = await apiLogin(email, password);
        token = data.access_token;
        userData = data.user || { email };
      } else {
        await apiRegister(email, password);
        const data = await apiLogin(email, password);
        token = data.access_token;
        userData = data.user || { email };
      }
      
      login(token, userData);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Authentication failed");
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

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full mt-6"
            style={{
              backgroundColor: loading ? "rgba(58, 107, 74, 0.6)" : "var(--color-accent)",
              color: "#fff",
              width: "100%",
              height: "40px",
              borderRadius: "var(--radius-md)",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
              fontFamily: "inherit",
              fontSize: "12px",
            }}
          >
            {loading ? "Processing..." : isLogin ? "Sign in" : "Create account"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            style={{
              background: "none",
              border: "none",
              color: "var(--color-text-primary)",
              textDecoration: "underline",
              cursor: "pointer",
            }}
          >
            {isLogin ? "Create account" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}

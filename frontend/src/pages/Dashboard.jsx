import { useAnalyze } from "../hooks/useAnalyze";
import PaymentForm from "../components/PaymentForm";
import ResultsPanel from "../components/ResultsPanel";
import AuthPanel from "../components/AuthPanel";
import QueryRecap from "../components/QueryRecap";

export default function Dashboard({ token, user, onLogin, onLogout }) {
  const { form, updateField, loading, error, result, submit, resetResult } = useAnalyze();
  const hasResult = result !== null;

  // Initials for avatar
  const initials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : "FN";

  return (
    <div className="flex flex-col min-h-screen" style={{ backgroundColor: "var(--color-canvas)", fontFamily: "-apple-system,'Segoe UI',sans-serif" }}>

      {/* ── Nav ─────────────────────────────────────────────────── */}
      <nav
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "0 32px", height: "52px",
          background: "#fff", borderBottom: "0.5px solid var(--color-border)",
        }}
      >
        {/* Wordmark: Fin + accent "o" + va */}
        <div
          className="font-display"
          style={{ fontWeight: 700, fontSize: "23px", letterSpacing: "0.01em", color: "var(--color-text-primary)" }}
        >
          Fin<span style={{ color: "var(--color-accent)" }}>o</span>va
        </div>

        {/* Auth area */}
        {token ? (
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span className="font-mono-custom" style={{ fontSize: "11px", color: "#9A9690" }}>
              {user?.email ?? ""}
            </span>
            {/* Avatar circle */}
            <button
              onClick={onLogout}
              title="Sign out"
              style={{
                width: "28px", height: "28px", borderRadius: "50%",
                background: "var(--color-accent-light)",
                border: "none", cursor: "pointer",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "'DM Mono', monospace", fontSize: "9px",
                color: "var(--color-accent)", fontWeight: 500,
              }}
            >
              {initials}
            </button>
          </div>
        ) : (
          <a href="#" className="btn-ghost" style={{ fontSize: "12px" }}>Sign in</a>
        )}
      </nav>

      {/* ── Query recap bar (results mode only) ─────────────────── */}
      {hasResult && token && (
        <QueryRecap form={form} result={result} onEdit={resetResult} />
      )}

      {/* ── Main ─────────────────────────────────────────────────── */}
      <main style={{ flex: 1, backgroundColor: "var(--color-canvas)" }}>
        {!token ? (
          <AuthPanel onLogin={onLogin} />
        ) : hasResult ? (
          <div
            className="anim-fade-up"
            style={{ maxWidth: "860px", margin: "0 auto", padding: "32px 40px 64px" }}
          >
            <ResultsPanel result={result} form={form} />
          </div>
        ) : (
          <div style={{ maxWidth: "480px", margin: "0 auto", padding: "36px 40px" }}>
            <PaymentForm
              form={form}
              updateField={updateField}
              loading={loading}
              error={error}
              onSubmit={() => submit(token)}
            />
          </div>
        )}
      </main>

      {/* ── Footer ───────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: "0.5px solid var(--color-border)",
          padding: "12px 32px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
        }}
      >
        <span className="font-mono-custom" style={{ fontSize: "11px", color: "#B0AAA2" }}>
          Finova · rates via ExchangeRate-API
        </span>
      </footer>
    </div>
  );
}

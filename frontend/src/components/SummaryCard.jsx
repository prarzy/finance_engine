/**
 * SummaryCard — v4 rec-card extended for multi-hop routes.
 * Shows full RoutePathFlow instead of just the method name.
 */
import RoutePathFlow from "./RoutePathFlow";
import { fmt, formatMethodName } from "../utils/routeUtils";

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

function BreakdownBar({ label, value, worstCost, color }) {
  const w = worstCost > 0 ? Math.min((value / worstCost) * 100, 100) : 0;
  return (
    <div>
      <div style={{ fontSize: "10px", color: "#A8A39C", letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: "4px" }}>
        {label}
      </div>
      <div style={{ height: "4px", background: "#EAE6DF", borderRadius: "2px", marginBottom: "6px", overflow: "hidden" }}>
        <div style={{ width: `${w}%`, height: "100%", background: color, borderRadius: "2px" }} />
      </div>
      <div style={{ fontFamily: MONO, fontSize: "13px", color: "var(--color-text-primary)" }}>
        {fmt(value)}
      </div>
    </div>
  );
}

export default function SummaryCard({ route, amountUsd, worstCost }) {
  if (!route) return null;

  const isInstant = route.processing_days === 0;
  const fees      = (route.fixed_fee_usd ?? 0) + (route.variable_fee_usd ?? 0);
  const noFixed   = (route.fixed_fee_usd ?? 0) === 0;
  const hasPath   = Array.isArray(route.path) && route.path.length > 0;
  const hopCount  = route.hop_count ?? 1;
  const methodDisplay = formatMethodName(route.method_name ?? "");

  return (
    <div className="card-best" style={{ padding: "24px 28px" }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>

        {/* ── Left ── */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* RECOMMENDED pill */}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "5px",
            background: "var(--color-accent-light)", color: "var(--color-accent-dark)",
            fontSize: "10px", fontFamily: MONO, letterSpacing: "0.08em",
            padding: "3px 10px", borderRadius: "4px", marginBottom: "12px",
          }}>
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <path d="M5 1l1 2.5L8.5 4 6.5 6l.5 2.5L5 7.2 3 8.5l.5-2.5L1.5 4 4 3.5 5 1z"
                stroke="#2C5940" strokeWidth="1" strokeLinejoin="round" />
            </svg>
            RECOMMENDED
          </div>

          {/* Route path or method name */}
          <div style={{ marginBottom: "12px" }}>
            {hasPath ? (
              <RoutePathFlow path={route.path} />
            ) : (
              <div className="text-heading-3" style={{ color: "var(--color-text-primary)" }}>
                {methodDisplay}
              </div>
            )}
          </div>

          {/* Badges row */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>

            {/* Settlement */}
            <span style={{
              display: "inline-flex", alignItems: "center", gap: "4px",
              fontSize: "11px", padding: "4px 10px", borderRadius: "20px",
              color: isInstant ? "var(--color-accent)" : "#7A7570",
              background: isInstant ? "var(--color-accent-light)" : "#F5F2EC",
              border: `0.5px solid ${isInstant ? "var(--color-accent-border)" : "var(--color-border)"}`,
            }}>
              {isInstant ? (
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <path d="M6 1L4 5.5h2.5L4.5 9" stroke="var(--color-accent)" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
              ) : (
                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                  <circle cx="6" cy="6" r="4" stroke="#7A7570" strokeWidth="1.2" />
                  <path d="M6 3v2l1.5 1.5" stroke="#7A7570" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
              )}
              {isInstant ? "Instant settlement" : `${route.processing_days} business day${route.processing_days > 1 ? "s" : ""}`}
            </span>

            {/* Spread (only for single-hop) */}
            {hopCount === 1 && (
              <span style={{
                display: "inline-flex", alignItems: "center",
                fontSize: "11px", padding: "4px 10px", borderRadius: "20px",
                color: "#7A7570", background: "#F5F2EC", border: "0.5px solid var(--color-border)",
                fontFamily: MONO,
              }}>
                {Number(route.fx_spread_pct ?? 0).toFixed(2)}% FX spread
              </span>
            )}

            {/* Hop count */}
            {hopCount > 1 && (
              <span style={{
                display: "inline-flex", alignItems: "center", gap: "4px",
                fontSize: "11px", padding: "4px 10px", borderRadius: "20px",
                color: "#7A7570", background: "#F5F2EC", border: "0.5px solid var(--color-border)",
                fontFamily: MONO,
              }}>
                <svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M2 8h4l2-4 2 8 2-4h2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {hopCount} hops
              </span>
            )}

            {/* Fixed fee / no fee (single-hop only) */}
            {hopCount === 1 && (
              <span style={{
                display: "inline-flex", alignItems: "center",
                fontSize: "11px", padding: "4px 10px", borderRadius: "20px",
                color: "#7A7570", background: "#F5F2EC", border: "0.5px solid var(--color-border)",
                fontFamily: MONO,
              }}>
                {noFixed ? "No fixed fee" : `${fmt(route.fixed_fee_usd)} fixed fee`}
              </span>
            )}
          </div>
        </div>

        {/* ── Right: total cost ── */}
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: "10px", color: "#A8A39C", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: "4px" }}>
            Total cost
          </div>
          <div className="text-cost-large">
            {fmt(route.total_cost_usd)}
          </div>
          {amountUsd != null && (
            <div style={{ fontSize: "11px", color: "#A8A39C", marginTop: "4px", fontFamily: MONO }}>
              on {fmt(amountUsd)} transfer
            </div>
          )}
        </div>
      </div>

      {/* ── Breakdown bars ── */}
      <div style={{
        marginTop: "20px", paddingTop: "16px",
        borderTop: "0.5px solid #EAE6DF",
        display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px",
      }}>
        <BreakdownBar label="FX Cost"  value={route.fx_cost_usd ?? 0}    worstCost={worstCost} color="var(--color-bar-fx)" />
        <BreakdownBar label="Fees"     value={fees}                       worstCost={worstCost} color="var(--color-bar-fees)" />
        <BreakdownBar label="Total"    value={route.total_cost_usd ?? 0}  worstCost={worstCost} color="var(--color-bar-total)" />
      </div>

      {/* ── Why This Route? — Explanations ── */}
      {route.explanations && route.explanations.length > 0 && (
        <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: "0.5px solid #EAE6DF" }}>
          <p style={{
            fontSize: "9px",
            color: "#B0AAA2",
            letterSpacing: "0.04em",
            textTransform: "uppercase",
            marginBottom: "8px",
            fontWeight: 600,
          }}>
            Why This Route?
          </p>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "6px" }}>
            {route.explanations.map((exp, i) => (
              <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "13px", color: "#7A7570", lineHeight: "1.5" }}>
                <span style={{ color: "#7A7570", flexShrink: 0, marginTop: "1px" }}>✓</span>
                <span>{exp}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

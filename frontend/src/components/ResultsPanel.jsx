/**
 * ResultsPanel — full-width results layout.
 * Renders: savings ribbon → recommended hero → route comparison table.
 */
import SummaryCard   from "./SummaryCard";
import RouteCardList from "./RouteCardList";

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

function fmt(n) {
  return "$" + Number(n ?? 0).toFixed(2);
}
function formatTimestamp(ts) {
  if (!ts) return null;
  try { return new Date(ts).toUTCString().slice(17, 22) + " UTC"; }
  catch { return null; }
}

export default function ResultsPanel({ result }) {
  if (!result) return null;

  const hasSavings   = (result.savings_vs_worst_usd ?? 0) > 0;
  const hasRoutes    = Array.isArray(result.all_routes) && result.all_routes.length > 0;
  const worstCost    = hasRoutes
    ? result.all_routes[result.all_routes.length - 1].total_cost_usd
    : 0;
  const bestLabel    = (result.recommended?.method_name ?? "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
  const maxHops      = hasRoutes
    ? Math.max(...result.all_routes.map((r) => r.hop_count ?? 1))
    : 1;
  const ts           = formatTimestamp(result.timestamp);

  return (
    <section aria-label="Analysis results">

      {/* ── Savings ribbon ── */}
      {hasSavings && (
        <div
          className="anim-fade-up"
          style={{
            background: "var(--color-accent-light)",
            border: "0.5px solid var(--color-accent-border)",
            borderRadius: "var(--radius-lg)",
            padding: "12px 20px",
            marginBottom: "20px",
            display: "flex", alignItems: "center", justifyContent: "space-between",
            flexWrap: "wrap", gap: "8px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{
              width: "32px", height: "32px", borderRadius: "8px",
              background: "var(--color-accent)", flexShrink: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 2l1.5 3.5L13 6l-2.5 2.5.6 3.5L8 10.5 4.9 12l.6-3.5L3 6l3.5-.5L8 2z"
                  stroke="#EEF5F0" strokeWidth="1.2" strokeLinejoin="round" />
              </svg>
            </div>
            <div style={{ fontSize: "13px", color: "var(--color-text-primary)" }}>
              Using{" "}
              <strong style={{ fontFamily: "'Cormorant Garamond',Georgia,serif", fontSize: "18px", fontWeight: 600, color: "var(--color-accent-dark)" }}>
                {bestLabel}
              </strong>{" "}
              saves you{" "}
              <strong style={{ fontFamily: "'Cormorant Garamond',Georgia,serif", fontSize: "18px", fontWeight: 600, color: "var(--color-accent-dark)" }}>
                {fmt(result.savings_vs_worst_usd)}
              </strong>{" "}
              compared to the most expensive option
            </div>
          </div>
          {ts && (
            <div style={{ fontFamily: MONO, fontSize: "11px", color: "#7A9E85", flexShrink: 0 }}>
              as of {ts}
            </div>
          )}
        </div>
      )}

      {/* ── Multi-hop context note ── */}
      {maxHops > 1 && (
        <div
          className="anim-fade-up"
          style={{
            animationDelay: "30ms",
            display: "flex", alignItems: "center", gap: "7px",
            marginBottom: "16px",
            fontFamily: MONO, fontSize: "11px", color: "#9A9690",
          }}
        >
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M2 8h4l2-4 2 8 2-4h2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Multi-hop routes found — money flows through intermediate currencies to reduce cost
        </div>
      )}

      {/* ── Recommended card ── */}
      {result.recommended && (
        <div className="anim-fade-up" style={{ animationDelay: "60ms", marginBottom: "20px" }}>
          <SummaryCard
            route={result.recommended}
            amountUsd={result.amount_usd}
            worstCost={worstCost}
          />
        </div>
      )}

      {/* ── All routes ── */}
      {hasRoutes && (
        <div className="anim-fade-up" style={{ animationDelay: "120ms" }}>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            marginBottom: "12px",
          }}>
            <span style={{ fontSize: "11px", color: "#A8A39C", letterSpacing: "0.07em", textTransform: "uppercase" }}>
              All routes
            </span>
            <span style={{ fontFamily: MONO, fontSize: "11px", color: "#C4BEB6" }}>
              {result.all_routes.length} routes ranked by total cost
            </span>
          </div>
          <RouteCardList routes={result.all_routes} />
        </div>
      )}

      {/* ── Footer ── */}
      {(result.mid_market_rate || result.amount_usd) && (
        <div style={{ marginTop: "16px" }}>
          <span style={{ fontFamily: MONO, fontSize: "11px", color: "#B0AAA2" }}>
            {result.mid_market_rate && `Mid-market rate: ${result.mid_market_rate}`}
            {result.mid_market_rate && result.amount_usd && "  ·  "}
            {result.amount_usd && `Amount (USD): ${fmt(result.amount_usd)}`}
            {ts && `  ·  as of ${ts}`}
          </span>
        </div>
      )}
    </section>
  );
}

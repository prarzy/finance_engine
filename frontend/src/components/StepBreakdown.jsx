/**
 * StepBreakdown — collapsible per-hop cost breakdown.
 *
 * Props:
 *   steps    : RouteStep[]
 *   open     : boolean
 *   onToggle : () => void
 */
import { fmt, formatMethodName } from "../utils/routeUtils";

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

function ChevronDown({ open }) {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
      stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"
      style={{ transition: "transform 180ms ease", transform: open ? "rotate(180deg)" : "none", flexShrink: 0 }}>
      <path d="M2 4l4 4 4-4" />
    </svg>
  );
}

export default function StepBreakdown({ steps = [], open, onToggle }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div>
      {/* Toggle button */}
      <button
        onClick={onToggle}
        style={{
          display: "flex", alignItems: "center", gap: "5px",
          background: "none", border: "none", cursor: "pointer",
          fontSize: "11px", color: "var(--color-text-muted)",
          fontFamily: MONO, padding: "6px 0 0",
        }}
      >
        <ChevronDown open={open} />
        {open ? "Hide" : "Show"} step breakdown
      </button>

      {open && (
        <div style={{
          marginTop: "10px",
          paddingTop: "10px",
          borderTop: "0.5px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}>
          {steps.map((step, i) => (
            <div key={i} style={{
              display: "grid",
              gridTemplateColumns: "20px 1fr auto",
              alignItems: "start",
              gap: "10px",
            }}>
              {/* Step number */}
              <div style={{
                width: "20px", height: "20px",
                borderRadius: "50%",
                background: "var(--color-accent-light)",
                border: "0.5px solid var(--color-accent-border)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: MONO, fontSize: "9px",
                color: "var(--color-accent-dark)", fontWeight: 500,
                flexShrink: 0,
              }}>
                {i + 1}
              </div>

              {/* Method + currency path */}
              <div>
                <div style={{ fontWeight: 500, fontSize: "12px", color: "var(--color-text-primary)", marginBottom: "3px" }}>
                  {formatMethodName(step.method)}
                </div>
                <div style={{ fontFamily: MONO, fontSize: "11px", color: "var(--color-text-muted)" }}>
                  {step.from_currency} → {step.to_currency}
                </div>
                {/* Mini cost breakdown */}
                <div style={{
                  display: "flex", gap: "8px", flexWrap: "wrap",
                  marginTop: "4px",
                }}>
                  {[
                    { label: "FX", value: step.fx_cost_usd },
                    { label: "Fee", value: step.fixed_fee_usd + step.variable_fee_usd },
                  ].filter(x => x.value > 0).map(({ label, value }) => (
                    <span key={label} style={{
                      fontFamily: MONO, fontSize: "10px",
                      color: "#9A9690",
                    }}>
                      {label}: {fmt(value)}
                    </span>
                  ))}
                  {step.processing_days === 0 ? (
                    <span style={{ fontSize: "10px", color: "var(--color-accent)", fontFamily: MONO }}>⚡ Instant</span>
                  ) : (
                    <span style={{ fontSize: "10px", color: "#9A9690", fontFamily: MONO }}>⏱ {step.processing_days}d</span>
                  )}
                </div>
              </div>

              {/* Step cost */}
              <div style={{
                fontFamily: MONO, fontSize: "13px", fontWeight: 500,
                color: "var(--color-text-primary)", flexShrink: 0,
                textAlign: "right",
              }}>
                {fmt(step.step_cost_usd)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

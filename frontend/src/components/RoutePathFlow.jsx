/**
 * RoutePathFlow — horizontal path visualization.
 *
 * Renders: [INR] → [Bank Transfer] → [USD] → [Revolut] → [EUR]
 *
 * Props:
 *   path    : string[]   raw path array from backend
 *   compact : boolean    smaller size for route list rows
 */
import { parsePath } from "../utils/routeUtils";

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

function ArrowRight({ size = 12 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      style={{ flexShrink: 0 }}>
      <path d="M3 8h10M9.5 5l3 3-3 3" />
    </svg>
  );
}

export default function RoutePathFlow({ path = [], compact = false }) {
  // Fallback: if no path, show nothing
  if (!path || path.length === 0) return null;

  const segments = parsePath(path);

  return (
    <div style={{
      display: "flex", alignItems: "center", flexWrap: "wrap",
      gap: compact ? "4px" : "6px",
    }}>
      {segments.map((seg, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: compact ? "4px" : "6px" }}>
          {/* Arrow between segments */}
          {i > 0 && (
            <span style={{ color: "#C4BEB6" }}>
              <ArrowRight size={compact ? 10 : 12} />
            </span>
          )}

          {seg.type === "currency" ? (
            /* Currency badge */
            <span style={{
              fontFamily: MONO,
              fontSize: compact ? "10px" : "12px",
              fontWeight: 500,
              color: "var(--color-text-primary)",
              background: "#F5F2EC",
              border: "0.5px solid var(--color-border-mid)",
              borderRadius: "4px",
              padding: compact ? "2px 6px" : "3px 8px",
              letterSpacing: "0.04em",
              flexShrink: 0,
            }}>
              {seg.label}
            </span>
          ) : (
            /* Method pill */
            <span style={{
              fontFamily: "-apple-system,'Segoe UI',sans-serif",
              fontSize: compact ? "10px" : "11px",
              fontWeight: 500,
              color: "var(--color-accent-dark)",
              background: "var(--color-accent-light)",
              border: "0.5px solid var(--color-accent-border)",
              borderRadius: "20px",
              padding: compact ? "2px 8px" : "3px 10px",
              flexShrink: 0,
              whiteSpace: "nowrap",
            }}>
              {seg.label}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

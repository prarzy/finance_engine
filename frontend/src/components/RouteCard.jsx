/**
 * RouteCard — v4 grid layout extended for multi-hop routes.
 *
 * Layout: [rank | body (path + bars) | total cost]
 * Body now shows RoutePathFlow + StepBreakdown (collapsible).
 * Falls back to old method_name display if path is absent.
 */
import { useState } from "react";
import RoutePathFlow from "./RoutePathFlow";
import StepBreakdown from "./StepBreakdown";
import { fmt, formatMethodName } from "../utils/routeUtils";

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

export default function RouteCard({ route, worstCost, index }) {
  const [stepsOpen, setStepsOpen] = useState(false);
  if (!route) return null;

  const isBest     = route.is_recommended === true;
  const isInstant  = route.processing_days === 0;
  const fees       = (route.fixed_fee_usd ?? 0) + (route.variable_fee_usd ?? 0);
  const wt         = worstCost || 1;
  const hasPath    = Array.isArray(route.path) && route.path.length > 0;
  const hasSteps   = Array.isArray(route.steps) && route.steps.length > 0;
  const hopCount   = route.hop_count ?? 1;

  // Mini bar widths (relative to worst route)
  const fxW  = Math.min(((route.fx_cost_usd ?? 0) / wt) * 100, 100).toFixed(1);
  const feW  = Math.min((fees / wt) * 100, 100).toFixed(1);
  const totW = Math.min(((route.total_cost_usd ?? 0) / wt) * 100, 100).toFixed(1);

  const settleText = isInstant
    ? { symbol: "⚡", label: "Instant", color: "#A8A39C" }
    : { symbol: "⏱", label: `${route.processing_days}d`, color: "#A8A39C" };

  return (
    <div
      className="route-card-v4 anim-fade-up"
      style={{
        animationDelay: `${index * 45}ms`,
        transition: "box-shadow 140ms ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.boxShadow = "0 2px 10px rgba(0,0,0,0.06)")}
      onMouseLeave={(e) => (e.currentTarget.style.boxShadow = "none")}
    >
      {/* ── Rank column ── */}
      <div className="rc-rank-col">
        <span style={{ fontFamily: MONO, fontSize: "11px", color: "#C4BEB6" }}>
          #{route.rank ?? index + 1}
        </span>
      </div>

      {/* ── Body ── */}
      <div style={{ padding: "14px 16px" }}>

        {/* Top row: path + badges */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px", flexWrap: "wrap" }}>
          {isBest && (
            <span style={{
              background: "var(--color-accent-light)", color: "var(--color-accent-dark)",
              fontSize: "10px", padding: "2px 8px", borderRadius: "4px",
              fontFamily: MONO, flexShrink: 0,
            }}>
              Best
            </span>
          )}
          {hopCount > 1 && (
            <span style={{
              background: "#F5F2EC", color: "#7A7570",
              fontSize: "10px", padding: "2px 8px", borderRadius: "4px",
              fontFamily: MONO, border: "0.5px solid var(--color-border)",
              flexShrink: 0,
            }}>
              {hopCount} hops
            </span>
          )}
          <span style={{
            display: "flex", alignItems: "center", gap: "3px",
            fontSize: "11px", color: settleText.color, fontFamily: MONO,
            flexShrink: 0,
          }}>
            {settleText.symbol} {settleText.label}
          </span>
        </div>

        {/* Route path visualization OR fallback method name */}
        <div style={{ marginBottom: "10px" }}>
          {hasPath ? (
            <RoutePathFlow path={route.path} compact />
          ) : (
            <span style={{ fontSize: "14px", fontWeight: 500, color: "var(--color-text-primary)" }}>
              {formatMethodName(route.method_name ?? "")}
            </span>
          )}
        </div>

        {/* Mini bars: FX / Fees / Total */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
          {[
            { label: "FX",    w: fxW,  val: route.fx_cost_usd ?? 0, color: "var(--color-bar-fx)" },
            { label: "Fees",  w: feW,  val: fees,                    color: "var(--color-bar-fees)" },
            { label: "Total", w: totW, val: route.total_cost_usd ?? 0, color: "var(--color-bar-total)" },
          ].map(({ label, w, val, color }) => (
            <div key={label}>
              <div style={{ fontSize: "9px", color: "#B0AAA2", letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: "4px" }}>
                {label}
              </div>
              <div style={{ height: "3px", background: "#EDEAE4", borderRadius: "2px", marginBottom: "4px", overflow: "hidden" }}>
                <div style={{ width: `${w}%`, height: "100%", background: color, borderRadius: "2px" }} />
              </div>
              <div style={{ fontFamily: MONO, fontSize: "11px", color: "#7A7570" }}>
                {fmt(val)}
              </div>
            </div>
          ))}
        </div>

        {/* Collapsible step breakdown */}
        {hasSteps && (
          <StepBreakdown
            steps={route.steps}
            open={stepsOpen}
            onToggle={() => setStepsOpen(!stepsOpen)}
          />
        )}
      </div>

      {/* ── Total cost column ── */}
      <div className="rc-total-col">
        <div>
          <div style={{ fontSize: "9px", color: "#B0AAA2", letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: "3px" }}>
            Cost
          </div>
          <div className="text-cost-medium">
            {fmt(route.total_cost_usd)}
          </div>
        </div>
      </div>
    </div>
  );
}

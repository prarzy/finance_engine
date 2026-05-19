import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from "recharts";

/**
 * CostBreakdown — Recharts horizontal bar chart with redesigned colors
 *
 * Props:
 *   route     : RouteOut
 *   worstCost : number
 */
export default function CostBreakdown({ route, worstCost }) {
  if (!route || worstCost === 0) {
    return (
      <p className="text-xs text-center py-2" style={{ color: "var(--color-text-muted)" }}>
        $0.00 total cost
      </p>
    );
  }

  const fees = route.fixed_fee_usd + route.variable_fee_usd;

  const data = [
    { name: "FX Cost", value: route.fx_cost_usd },
    { name: "Fees", value: fees },
    { name: "Total", value: route.total_cost_usd },
  ];

  // New redesigned colors from design tokens
  const COLORS = [
    "var(--color-bar-fx)",    // #8FA4C0 muted blue
    "var(--color-bar-fees)",  // #C4A882 warm sand
    "var(--color-bar-total)", // #7A9E80 sage
  ];

  // Resolve CSS custom properties to actual hex values for Recharts
  const resolvedColors = [
    "#8FA4C0", // FX Cost — muted blue
    "#C4A882", // Fees — warm sand
    "#7A9E80", // Total — sage
  ];

  return (
    <div>
      {/* Labels row */}
      <div className="flex justify-between mb-2" style={{ fontSize: "11px" }}>
        <div className="flex gap-4">
          {["FX Cost", "Fees", "Total"].map((label, i) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <div
                style={{
                  width: "8px",
                  height: "8px",
                  backgroundColor: resolvedColors[i],
                  borderRadius: "1px",
                }}
              ></div>
              <span style={{ color: "var(--color-text-secondary)" }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={88}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 8, bottom: 0, left: 0 }}
        >
          <XAxis
            type="number"
            domain={[0, worstCost]}
            hide
          />
          <YAxis
            type="category"
            dataKey="name"
            width={0}
            tick={false}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(0,0,0,0.02)" }}
            formatter={(v) => [`$${Number(v).toFixed(2)}`, ""]}
            contentStyle={{
              background: "var(--color-surface)",
              border: "0.5px solid var(--color-border)",
              borderRadius: "var(--radius-md)",
              fontSize: "12px",
              color: "var(--color-text-primary)",
              boxShadow: "none",
            }}
          />
          <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={14}>
            {data.map((_, i) => (
              <Cell key={i} fill={resolvedColors[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Totals row below chart */}
      <div
        style={{
          borderTop: "0.5px solid var(--color-border)",
          marginTop: "8px",
          paddingTop: "8px",
          display: "flex",
          justifyContent: "space-between",
          fontSize: "13px",
        }}
      >
        <span style={{ color: "var(--color-text-secondary)" }}>Total</span>
        <span
          className="text-cost-small"
          style={{ color: "var(--color-text-primary)" }}
        >
          {route.total_cost_usd ? `$${route.total_cost_usd.toFixed(2)}` : "$0.00"}
        </span>
      </div>
    </div>
  );
}

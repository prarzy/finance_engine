import { formatUSD, formatPct } from "../utils/formatters";

/**
 * SavingsBadge — displays savings_vs_worst_usd / _pct
 *
 * Props:
 *   usd : number
 *   pct : number
 */
export default function SavingsBadge({ usd, pct }) {
  return (
    <div
      className="flex items-baseline gap-1"
      style={{
        flexWrap: "wrap",
        justifyContent: "flex-start",
      }}
    >
      {/* "Save up to $X.XX" in Playfair italic */}
      <span
        style={{
          fontFamily: "'Cormorant Garamond', Georgia, serif",
          fontWeight: 500,
          fontStyle: "italic",
          fontSize: "18px",
          color: "var(--color-text-accent)",
        }}
      >
        Save up to {formatUSD(usd)}
      </span>

      {/* Separator dot */}
      <span style={{ color: "var(--color-text-secondary)" }}>·</span>

      {/* "X% vs slowest" in small body */}
      <span
        className="text-sm"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {formatPct(pct)} vs the slowest route
      </span>
    </div>
  );
}

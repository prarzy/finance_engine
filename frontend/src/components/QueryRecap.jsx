/**
 * QueryRecap — v4 "summary-bar" above results.
 * Shows: amount · currency pair · method count · mid-market rate · [Edit]
 */
const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

export default function QueryRecap({ form, result, onEdit }) {
  const methodCount = form.available_methods ? form.available_methods.length : 7;
  const rawAmount   = String(form.amount).replace(/,/g, "");
  const displayAmount = Number(rawAmount).toLocaleString("en-US");
  const timestamp = result?.timestamp
    ? new Date(result.timestamp).toUTCString().slice(17, 22) + " UTC"
    : null;

  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "12px",
        border: "0.5px solid var(--color-border)",
        padding: "18px 24px",
        margin: "0 auto 8px",
        maxWidth: "860px",
        marginTop: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "12px",
      }}
    >
      {/* Left */}
      <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
        {/* Big amount */}
        <div
          className="font-display"
          style={{ fontWeight: 600, fontSize: "28px", color: "var(--color-text-primary)", lineHeight: 1 }}
        >
          {form.source_currency === "USD" ? "$" : ""}{displayAmount}
        </div>
        {/* Pair + method count */}
        <div
          style={{
            marginLeft: "12px", paddingLeft: "12px",
            borderLeft: "0.5px solid var(--color-border)",
            fontFamily: MONO, fontSize: "12px",
            color: "#9A9690", lineHeight: 1.5,
          }}
        >
          <div style={{ marginBottom: "2px" }}>
            {form.source_currency} → {form.target_currency}
          </div>
          <div style={{ fontSize: "14px", color: "var(--color-text-primary)", fontWeight: 500, letterSpacing: "0.04em" }}>
            {methodCount} method{methodCount !== 1 ? "s" : ""} compared
          </div>
        </div>
      </div>

      {/* Right */}
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        {result?.mid_market_rate && (
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "10px", color: "#A8A39C", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: "2px" }}>
              Mid-market rate
            </div>
            <div style={{ fontFamily: MONO, fontSize: "12px", color: "var(--color-text-primary)" }}>
              1 {form.source_currency} = {result.mid_market_rate} {form.target_currency}
            </div>
          </div>
        )}
        <button className="btn-edit" onClick={onEdit}>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M8 10L4 6l4-4" stroke="#7A7570" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Edit
        </button>
      </div>
    </div>
  );
}

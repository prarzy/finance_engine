/**
 * PaymentForm — v4 design with dynamic currency dropdowns.
 */

const CURRENCIES = [
  { code: "USD", symbol: "$",    name: "US Dollar"        },
  { code: "EUR", symbol: "€",    name: "Euro"             },
  { code: "GBP", symbol: "£",    name: "British Pound"    },
  { code: "INR", symbol: "₹",    name: "Indian Rupee"     },
  { code: "AED", symbol: "د.إ",  name: "UAE Dirham"       },
  { code: "SGD", symbol: "S$",   name: "Singapore Dollar" },
  { code: "CAD", symbol: "C$",   name: "Canadian Dollar"  },
  { code: "AUD", symbol: "A$",   name: "Australian Dollar"},
  { code: "JPY", symbol: "¥",    name: "Japanese Yen"     },
];

const ALL_METHODS = [
  { key: "revolut",       label: "Revolut",       spread: "0.20%" },
  { key: "wise",          label: "Wise",           spread: "0.45%" },
  { key: "bank_transfer", label: "Bank Transfer",  spread: "1.50%" },
  { key: "paypal",        label: "PayPal",         spread: "3.00%" },
];

const MONO = "'DM Mono','Fira Mono',ui-monospace,monospace";

function symbolFor(code) {
  return CURRENCIES.find((c) => c.code === code)?.symbol ?? code;
}

function Checkmark() {
  return (
    <svg width="9" height="9" viewBox="0 0 9 9" fill="none">
      <path d="M1.5 4.5l2 2L7.5 2" stroke="#EEF5F0" strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Styled <select> wrapper matching the v4 joined-field design
function CurrencySelect({ id, value, onChange, disabled, borderRadius }) {
  return (
    <div style={{ position: "relative", flex: 1 }}>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{
          width: "100%", height: "48px",
          border: "0.5px solid var(--color-border-mid)",
          borderRadius,
          background: "#fff",
          padding: "0 28px 0 14px",
          fontFamily: MONO, fontSize: "14px",
          color: "var(--color-text-primary)",
          appearance: "none", outline: "none",
          cursor: "pointer",
        }}
        onFocus={(e) => (e.target.style.borderColor = "var(--color-accent)")}
        onBlur={(e)  => (e.target.style.borderColor = "var(--color-border-mid)")}
      >
        {CURRENCIES.map((c) => (
          <option key={c.code} value={c.code}>
            {c.code} — {c.name}
          </option>
        ))}
      </select>
      {/* Chevron icon */}
      <span style={{
        position: "absolute", right: "10px", top: "50%",
        transform: "translateY(-50%)", pointerEvents: "none",
        color: "#A8A39C",
      }}>
        <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
          <path d="M1.5 3.5L5 7L8.5 3.5" stroke="currentColor"
            strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    </div>
  );
}

export default function PaymentForm({ form, updateField, loading, error, onSubmit, limitResults = [], limitChecking = false, onCheckLimits = () => {} }) {
  const selectedSet = new Set(form.available_methods ?? ALL_METHODS.map((m) => m.key));
  const allChecked  = form.available_methods === null;
  const symbol      = symbolFor(form.source_currency ?? "USD");
  const sameCurrency = form.source_currency === form.target_currency;

  // Determine if we have any valid providers
  const anyValid = limitResults.length === 0 || limitResults.some(r => r.valid);
  const canSubmit = anyValid && !limitChecking && !loading && !sameCurrency;

  // Call onCheckLimits when amount changes
  const handleAmountChange = (e) => {
    updateField("amount", e.target.value);
    const methods = form.available_methods ?? ALL_METHODS.map((m) => m.key);
    if (methods.length > 0) {
      onCheckLimits(e.target.value, form.source_currency, form.target_currency, methods);
    }
  };

  // Re-run limit check when source currency changes
  const handleSourceCurrencyChange = (val) => {
    updateField("source_currency", val);
    const methods = form.available_methods ?? ALL_METHODS.map((m) => m.key);
    if (form.amount && methods.length > 0) {
      onCheckLimits(form.amount, val, form.target_currency, methods);
    }
  };

  // Re-run limit check when target currency changes
  const handleTargetCurrencyChange = (val) => {
    updateField("target_currency", val);
    const methods = form.available_methods ?? ALL_METHODS.map((m) => m.key);
    if (form.amount && methods.length > 0) {
      onCheckLimits(form.amount, form.source_currency, val, methods);
    }
  };

  function handleMethodToggle(key) {
    const next = new Set(selectedSet);
    next.has(key) ? next.delete(key) : next.add(key);
    const arr = ALL_METHODS.map((m) => m.key).filter((k) => next.has(k));
    const newMethods = arr.length === ALL_METHODS.length ? null : arr;
    updateField("available_methods", newMethods);
    // Trigger limit check with new methods
    const methodsToCheck = newMethods ?? ALL_METHODS.map((m) => m.key);
    if (form.amount && methodsToCheck.length > 0) {
      onCheckLimits(form.amount, form.source_currency, form.target_currency, methodsToCheck);
    }
  }

  function handleAmountBlur(e) {
    const raw = String(e.target.value).replace(/,/g, "");
    if (raw && !isNaN(Number(raw))) {
      e.target.value = Number(raw).toLocaleString("en-US");
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit();
  }

  return (
    <div>
      {/* Eyebrow + title */}
      <p style={{ fontSize: "11px", color: "#A8A39C", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "8px" }}>
        Payment optimizer
      </p>
      <h1 className="text-heading-1" style={{ marginBottom: "6px", color: "var(--color-text-primary)" }}>
        Analyze a transfer
      </h1>
      <p style={{ fontSize: "13px", color: "#9A9690", marginBottom: "28px", lineHeight: 1.6 }}>
        Compare live costs across every payment rail before you send. No hidden fees — just numbers.
      </p>
      <div style={{ height: "0.5px", background: "var(--color-border)", marginBottom: "28px" }} />

      <form onSubmit={handleSubmit} noValidate>

        {/* Error banner */}
        {error && (
          <div style={{
            marginBottom: "16px", padding: "10px 14px",
            background: "var(--color-error-bg)",
            border: "0.5px solid var(--color-error-border)",
            borderRadius: "var(--radius-md)",
            fontSize: "13px", color: "var(--color-error-text)",
          }}>
            {error}
          </div>
        )}

        {/* Same currency validation */}
        {sameCurrency && (
          <div style={{
            marginBottom: "16px", padding: "10px 14px",
            background: "#FEE2E2", border: "0.5px solid #FCA5A5",
            borderRadius: "var(--radius-md)",
            fontSize: "13px", color: "#7F1D1D",
          }}>
            Source and target currencies must be different.
          </div>
        )}

        {/* ── Amount ─────────────────────────────────────────────────────── */}
        <label style={{ fontSize: "10px", color: "#7A7570", letterSpacing: "0.07em", textTransform: "uppercase", display: "block", marginBottom: "7px" }}>
          Amount
        </label>
        <div style={{ position: "relative", marginBottom: "8px" }}>
          {/* Dynamic currency symbol */}
          <span style={{
            position: "absolute", left: "14px", top: "50%",
            transform: "translateY(-50%)",
            fontFamily: MONO, fontSize: "14px",
            color: "#B0AAA2", pointerEvents: "none",
            userSelect: "none",
          }}>
            {symbol}
          </span>
          <input
            id="amount"
            type="text"
            inputMode="decimal"
            placeholder="1,000.00"
            value={form.amount}
            onChange={handleAmountChange}
            onBlur={handleAmountBlur}
            disabled={loading}
            style={{
              width: "100%", height: "52px",
              border: "0.5px solid var(--color-border-mid)",
              borderRadius: "var(--radius-lg)",
              background: "#fff",
              /* Pad left enough for the widest symbol (د.إ) */
              paddingLeft: "38px", paddingRight: "14px",
              fontFamily: MONO, fontSize: "20px",
              color: "var(--color-text-primary)", outline: "none",
            }}
            onFocus={(e) => (e.target.style.borderColor = "var(--color-accent)")}
            onBlur={(e) => {
              e.target.style.borderColor = "var(--color-border-mid)";
              handleAmountBlur(e);
            }}
          />
        </div>

        {/* Limit warnings */}
        {limitResults.filter(r => !r.valid).length > 0 && (
          <div style={{ marginBottom: "16px", padding: "10px 14px", background: "#FEF3C7", border: "0.5px solid #F59E0B", borderRadius: "var(--radius-md)", fontSize: "12px", color: "#7C2D12" }}>
            {limitResults.filter(r => !r.valid).map((r, idx) => (
              <div key={idx} style={{ marginBottom: idx < limitResults.filter(r => !r.valid).length - 1 ? "6px" : 0 }}>
                <strong>{r.provider}:</strong> {r.error} {r.max_transfer_usd && `(max $${r.max_transfer_usd.toLocaleString()})`}
              </div>
            ))}
          </div>
        )}
        {!anyValid && limitResults.length > 0 && (
          <div style={{
            marginBottom: "16px", padding: "12px 14px",
            background: "#FEE2E2", border: "0.5px solid #FCA5A5",
            borderRadius: "var(--radius-md)",
            fontSize: "13px", color: "#7F1D1D",
          }}>
            No selected provider supports this amount for this corridor. Reduce the amount or select different providers.
          </div>
        )}

        {/* ── Currency pair ───────────────────────────────────────────────── */}
        <label style={{ fontSize: "10px", color: "#7A7570", letterSpacing: "0.07em", textTransform: "uppercase", display: "block", marginBottom: "7px" }}>
          Currency pair
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 40px 1fr", marginBottom: "28px" }}>

          {/* Source currency dropdown */}
          <CurrencySelect
            id="source_currency"
            value={form.source_currency}
            onChange={handleSourceCurrencyChange}
            disabled={loading}
            borderRadius="10px 0 0 10px"
          />

          {/* Arrow divider */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "center",
            height: "48px",
            background: "var(--color-surface-muted)",
            borderTop: "0.5px solid var(--color-border-mid)",
            borderBottom: "0.5px solid var(--color-border-mid)",
            color: "#C4BEB6",
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9.5 5l3 3-3 3" stroke="currentColor"
                strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          {/* Target currency dropdown */}
          <CurrencySelect
            id="target_currency"
            value={form.target_currency}
            onChange={handleTargetCurrencyChange}
            disabled={loading}
            borderRadius="0 10px 10px 0"
          />
        </div>

        {/* ── Payment methods ─────────────────────────────────────────────── */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
          <label style={{ fontSize: "10px", color: "#7A7570", letterSpacing: "0.07em", textTransform: "uppercase" }}>
            Payment methods
          </label>
          {!allChecked && (
            <button
              type="button"
              onClick={() => updateField("available_methods", null)}
              style={{ fontSize: "11px", color: "var(--color-accent)", background: "none", border: "none", cursor: "pointer", padding: 0 }}
            >
              Select all
            </button>
          )}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "32px" }}>
          {ALL_METHODS.map(({ key, label, spread }) => {
            const checked = selectedSet.has(key);
            return (
              <div
                key={key}
                className={`method-chip${checked ? " selected" : ""}`}
                onClick={() => !loading && handleMethodToggle(key)}
                role="checkbox"
                aria-checked={checked}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "13px", fontWeight: 500, color: "var(--color-text-primary)" }}>
                    {label}
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontFamily: MONO, fontSize: "10px", color: "#A8A39C" }}>{spread}</span>
                  <div className="chip-check">
                    {checked && <Checkmark />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Submit ──────────────────────────────────────────────────────── */}
        <button
          type="submit"
          disabled={!canSubmit}
          className="btn btn-primary"
          style={{ 
            height: "50px", 
            borderRadius: "var(--radius-lg)",
            opacity: !canSubmit ? 0.5 : 1,
            cursor: !canSubmit ? "not-allowed" : "pointer",
          }}
        >
          {limitChecking ? (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                style={{ animation: "spin 0.8s linear infinite" }}>
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
              Checking limits…
            </>
          ) : loading ? (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                style={{ animation: "spin 0.8s linear infinite" }}>
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
              Analyzing…
            </>
          ) : (
            <>
              Analyze routes
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2.5 7h9M8.5 4.5l3 2.5-3 2.5" stroke="#EEF5F0"
                  strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </>
          )}
        </button>
      </form>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

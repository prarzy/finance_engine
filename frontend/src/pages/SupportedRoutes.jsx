import { useState, useEffect } from "react";
import { API_BASE_URL } from "../services/api";

export default function SupportedRoutes() {
  const [data, setData] = useState(null);
  const [activeProvider, setActiveProvider] = useState("wise");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRoutes() {
      try {
        const response = await fetch(`${API_BASE_URL}/corridors`);
        if (!response.ok) throw new Error("Failed to load routes");
        const routeData = await response.json();
        setData(routeData);
        const firstProvider = Object.keys(routeData.corridors_by_provider || {})[0];
        if (firstProvider) setActiveProvider(firstProvider);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchRoutes();
  }, []);

  if (loading) {
    return <div style={{ padding: "32px", textAlign: "center", color: "#A8A39C" }}>Loading routes…</div>;
  }

  if (error) {
    return <div style={{ padding: "32px", color: "red" }}>Error: {error}</div>;
  }

  if (!data) return null;

  const corridors = (data.corridors_by_provider[activeProvider] || []).filter(c => {
    if (!search) return true;
    const q = search.toLowerCase();
    return c.source_currency.toLowerCase().includes(q) || c.target_currency.toLowerCase().includes(q);
  });

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 40px 64px" }}>
      <h1 style={{ fontSize: "40px", fontWeight: 300, color: "#1F1F1F", margin: "0 0 8px 0" }}>
        Supported Routes & Currencies
      </h1>
      <p style={{ fontSize: "13px", color: "#A8A39C", margin: "0 0 32px 0" }}>
        Real-time corridor support for each provider.
      </p>

      {/* Currencies */}
      <section style={{ marginBottom: "48px" }}>
        <h2 style={{ fontSize: "11px", color: "#A8A39C", textTransform: "uppercase", margin: "0 0 16px 0" }}>
          Currencies
        </h2>
        <div style={{ border: "0.5px solid #E5E0D8", borderRadius: "8px", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ backgroundColor: "#F9F9F9", borderBottom: "0.5px solid #E5E0D8" }}>
              <tr>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>Currency</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>Code</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>Can hold</th>
              </tr>
            </thead>
            <tbody>
              {data.currencies.map((c, idx) => (
                <tr key={c.code} style={{ borderBottom: idx < data.currencies.length - 1 ? "0.5px solid #E5E0D8" : "none" }}>
                  <td style={{ padding: "14px 16px", fontSize: "13px" }}><span style={{ marginRight: "8px" }}>{c.symbol}</span>{c.name}</td>
                  <td style={{ padding: "14px 16px", fontSize: "12px", fontFamily: "monospace", color: "#7A7570" }}>{c.code}</td>
                  <td style={{ padding: "14px 16px", fontSize: "13px", color: c.can_hold ? "#16A34A" : "#DC2626" }}>
                    {c.can_hold ? "✓ Yes" : "✗ No"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* KYC Info */}
      <section style={{ marginBottom: "48px" }}>
        <h2 style={{ fontSize: "11px", color: "#A8A39C", textTransform: "uppercase", margin: "0 0 16px 0" }}>
          Verification Tiers
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
          {[
            { tier: 0, name: "Unverified", desc: "No identity verification required. Suitable for small transactions." },
            { tier: 1, name: "Basic", desc: "Name and email verification. Covers most business payments." },
            { tier: 2, name: "Full", desc: "Complete KYC with documentation. Highest limits and best rates." },
          ].map(info => (
            <div
              key={info.tier}
              style={{
                border: "0.5px solid #E5E0D8",
                borderRadius: "8px",
                padding: "16px",
                backgroundColor: "#FAFAF8",
              }}
            >
              <div style={{ fontSize: "11px", color: "#A8A39C", textTransform: "uppercase", marginBottom: "6px" }}>
                Tier {info.tier}
              </div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "#1F1F1F", marginBottom: "8px" }}>
                {info.name}
              </div>
              <div style={{ fontSize: "12px", color: "#7A7570", lineHeight: "1.4" }}>
                {info.desc}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Corridors */}
      <section>
        <div style={{ display: "flex", gap: "8px", marginBottom: "16px", borderBottom: "0.5px solid #E5E0D8", paddingBottom: "12px" }}>
          {Object.keys(data.corridors_by_provider).map((slug) => (
            <button
              key={slug}
              onClick={() => { setActiveProvider(slug); setSearch(""); }}
              style={{
                padding: "10px 16px",
                border: "none",
                borderRadius: "6px",
                backgroundColor: activeProvider === slug ? "#E5E0D8" : "transparent",
                color: activeProvider === slug ? "#1F1F1F" : "#A8A39C",
                fontSize: "13px",
                cursor: "pointer",
              }}
            >
              {slug.charAt(0).toUpperCase() + slug.slice(1)}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: "16px", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "11px", color: "#A8A39C", textTransform: "uppercase", margin: 0 }}>Provider Corridors</h3>
          <input
            type="text"
            placeholder="Search…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              marginLeft: "auto",
              border: "0.5px solid #E5E0D8",
              borderRadius: "6px",
              padding: "8px 12px",
              fontSize: "12px",
              width: "200px",
            }}
          />
        </div>

        <div style={{ border: "0.5px solid #E5E0D8", borderRadius: "8px", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ backgroundColor: "#F9F9F9", borderBottom: "0.5px solid #E5E0D8" }}>
              <tr>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>From</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>To</th>
                <th style={{ padding: "12px 16px", textAlign: "right", fontSize: "10px", color: "#A8A39C" }}>Max</th>
                <th style={{ padding: "12px 16px", textAlign: "right", fontSize: "10px", color: "#A8A39C" }}>Min</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "10px", color: "#A8A39C" }}>KYC</th>
              </tr>
            </thead>
            <tbody>
              {corridors.length > 0 ? corridors.map((c, idx) => (
                <tr key={`${c.source_currency}-${c.target_currency}-${idx}`} style={{ borderBottom: idx < corridors.length - 1 ? "0.5px solid #E5E0D8" : "none" }}>
                  <td style={{ padding: "12px 16px", fontSize: "12px", fontFamily: "monospace" }}>{c.source_currency}</td>
                  <td style={{ padding: "12px 16px", fontSize: "12px", fontFamily: "monospace" }}>{c.target_currency}</td>
                  <td style={{ padding: "12px 16px", textAlign: "right", fontSize: "12px", color: "#7A7570" }}>
                    {c.max_transfer_usd ? `$${c.max_transfer_usd.toLocaleString()}` : "—"}
                  </td>
                  <td style={{ padding: "12px 16px", textAlign: "right", fontSize: "12px", color: "#7A7570" }}>
                    ${c.min_transfer_usd.toFixed(2)}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: "11px" }}>
                    <span style={{ padding: "4px 10px", borderRadius: "4px", backgroundColor: "#E5E0D8", color: "#7A7570" }}>
                      Tier {c.kyc_tier_required}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} style={{ padding: "32px", textAlign: "center", fontSize: "13px", color: "#A8A39C" }}>
                    No corridors found for "{search}"
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}


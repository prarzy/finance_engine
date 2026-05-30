import { useEffect, useState } from "react";
import { api } from "../services/api";

const PROVIDER_LABELS = {
  wise: "Wise",
  revolut: "Revolut",
  bank_transfer: "Bank Transfer",
  paypal: "PayPal",
};

const SETTLEMENT_LABEL = (hours) => {
  if (hours === 0) return "Instant";
  if (hours < 24) return `${hours}h`;
  return `${Math.round(hours / 24)}d`;
};

const PROVIDER_INFO = {
  wise: {
    note: "INR is supported as a source currency only (non-deliverable offshore). INR cannot be used as an intermediate or target.",
    source: "Verified: wise.com/help/articles/2897238",
  },
  revolut: {
    note: "INR transfers are supported outgoing to India only. Cannot be used as an intermediate hop.",
    source: "Verified: help.revolut.com/en-US/help/transfers/supported-countries-currencies",
  },
  bank_transfer: {
    note: "SWIFT-based. INR inbound remittances governed by RBI FEMA regulations. All other corridors via SWIFT international wire.",
    source: "RBI FEMA; SWIFT network",
  },
  paypal: {
    note: "INR is not supported in any direction (discontinued April 2021). Single transaction limit is $60,000 USD (may be reduced to $10,000 for some corridors).",
    source: "Verified: developer.paypal.com/api/nvp-soap/currency-codes; paypal.com/ai/cshelp",
  },
};

export default function SupportedRoutesPage() {
  const [data, setData] = useState(null);
  const [activeProvider, setActiveProvider] = useState("wise");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRoutes() {
      try {
        console.log("Fetching supported routes...");
        const routeData = await api.getSupportedRoutes();
        console.log("Received route data:", routeData);
        setData(routeData);
      } catch (err) {
        console.error("Failed to load routes:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchRoutes();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "32px", textAlign: "center", color: "#A8A39C", fontSize: "13px" }}>
        Loading supported routes…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        maxWidth: "1000px", 
        margin: "0 auto", 
        padding: "32px 40px",
      }}>
        <div style={{
          padding: "16px 20px",
          backgroundColor: "#FEE2E2",
          border: "0.5px solid #FCA5A5",
          borderRadius: "8px",
          color: "#7F1D1D",
          fontSize: "13px",
        }}>
          Error loading supported routes: {error}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const corridors = (data.corridors_by_provider[activeProvider] || []).filter(c => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      c.source_currency.toLowerCase().includes(q) ||
      c.target_currency.toLowerCase().includes(q)
    );
  });

  const providerInfo = PROVIDER_INFO[activeProvider];

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 40px 64px" }}>
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <h1 style={{
          fontFamily: "'Cormorant Garamond', serif",
          fontSize: "40px",
          fontWeight: 300,
          color: "#1F1F1F",
          margin: "0 0 8px 0",
        }}>
          Supported Routes & Currencies
        </h1>
        <p style={{
          fontSize: "13px",
          color: "#A8A39C",
          margin: 0,
          lineHeight: 1.6,
        }}>
          Real-time corridor support for each provider based on verified constraints and regulatory data.
        </p>
      </div>

      {/* Currencies table */}
      <section style={{ marginBottom: "48px" }}>
        <h2 style={{
          fontSize: "11px",
          color: "#A8A39C",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          margin: "0 0 16px 0",
          fontWeight: 500,
        }}>
          Currencies
        </h2>
        <div style={{
          border: "0.5px solid #E5E0D8",
          borderRadius: "8px",
          overflow: "hidden",
          backgroundColor: "#fff",
        }}>
          <table style={{
            width: "100%",
            borderCollapse: "collapse",
          }}>
            <thead style={{
              backgroundColor: "#F9F9F9",
              borderBottom: "0.5px solid #E5E0D8",
            }}>
              <tr>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Currency</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Code</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Can hold</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Can send from</th>
              </tr>
            </thead>
            <tbody>
              {data.currencies.map((c, idx) => (
                <tr
                  key={c.code}
                  style={{
                    borderBottom: idx < data.currencies.length - 1 ? "0.5px solid #E5E0D8" : "none",
                    transition: "background-color 0.2s",
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = "#F9F9F9"}
                  onMouseLeave={(e) => e.target.style.backgroundColor = "transparent"}
                >
                  <td style={{
                    padding: "14px 16px",
                    fontSize: "13px",
                    color: "#1F1F1F",
                  }}>
                    <span style={{ marginRight: "8px" }}>{c.symbol}</span>
                    {c.name}
                  </td>
                  <td style={{
                    padding: "14px 16px",
                    fontSize: "12px",
                    fontFamily: "'DM Mono', monospace",
                    color: "#7A7570",
                  }}>
                    {c.code}
                  </td>
                  <td style={{
                    padding: "14px 16px",
                    fontSize: "13px",
                    color: c.can_hold ? "#16A34A" : "#DC2626",
                  }}>
                    {c.can_hold ? "✓ Yes" : "✗ No"}
                  </td>
                  <td style={{
                    padding: "14px 16px",
                    fontSize: "13px",
                    color: "#16A34A",
                  }}>
                    ✓ Yes
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Provider corridors */}
      <section>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "16px",
        }}>
          <h2 style={{
            fontSize: "11px",
            color: "#A8A39C",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            margin: 0,
            fontWeight: 500,
          }}>
            Provider Corridors
          </h2>
          <input
            type="text"
            placeholder="Search corridor…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              backgroundColor: "#fff",
              border: "0.5px solid #E5E0D8",
              borderRadius: "6px",
              padding: "8px 12px",
              fontSize: "12px",
              color: "#1F1F1F",
              outline: "none",
              transition: "border-color 0.2s",
              width: "200px",
            }}
            onFocus={(e) => e.target.style.borderColor = "#1F1F1F"}
            onBlur={(e) => e.target.style.borderColor = "#E5E0D8"}
          />
        </div>

        {/* Provider tabs */}
        <div style={{
          display: "flex",
          gap: "8px",
          marginBottom: "16px",
          borderBottom: "0.5px solid #E5E0D8",
          paddingBottom: "12px",
        }}>
          {Object.keys(data.corridors_by_provider).map((slug) => (
            <button
              key={slug}
              onClick={() => {
                setActiveProvider(slug);
                setSearch("");
              }}
              style={{
                padding: "10px 16px",
                borderRadius: "6px",
                border: "none",
                backgroundColor: activeProvider === slug ? "#E5E0D8" : "transparent",
                color: activeProvider === slug ? "#1F1F1F" : "#A8A39C",
                fontSize: "13px",
                fontWeight: activeProvider === slug ? 500 : 400,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                if (activeProvider !== slug) {
                  e.target.style.color = "#1F1F1F";
                  e.target.style.backgroundColor = "#F5F5F5";
                }
              }}
              onMouseLeave={(e) => {
                if (activeProvider !== slug) {
                  e.target.style.color = "#A8A39C";
                  e.target.style.backgroundColor = "transparent";
                }
              }}
            >
              {PROVIDER_LABELS[slug] || slug}
            </button>
          ))}
        </div>

        {/* Provider info banner */}
        {providerInfo && (
          <div style={{
            backgroundColor: "#F9F9F9",
            border: "0.5px solid #E5E0D8",
            borderRadius: "8px",
            padding: "14px 16px",
            fontSize: "12px",
            color: "#7A7570",
            marginBottom: "16px",
            lineHeight: 1.5,
          }}>
            <p style={{ margin: "0 0 8px 0" }}>{providerInfo.note}</p>
            <p style={{ margin: 0, fontSize: "11px", color: "#A8A39C" }}>
              Source: {providerInfo.source}
            </p>
          </div>
        )}

        {/* Corridors table */}
        <div style={{
          border: "0.5px solid #E5E0D8",
          borderRadius: "8px",
          overflow: "hidden",
          backgroundColor: "#fff",
        }}>
          <table style={{
            width: "100%",
            borderCollapse: "collapse",
          }}>
            <thead style={{
              backgroundColor: "#F9F9F9",
              borderBottom: "0.5px solid #E5E0D8",
            }}>
              <tr>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>From</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>To</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "right",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Max (USD equiv.)</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "right",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Min (USD)</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>Settlement</th>
                <th style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  fontSize: "10px",
                  color: "#A8A39C",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 500,
                }}>KYC Required</th>
              </tr>
            </thead>
            <tbody>
              {corridors.length > 0 ? (
                corridors.map((c, idx) => (
                  <tr
                    key={`${c.source_currency}-${c.target_currency}-${idx}`}
                    style={{
                      borderBottom: idx < corridors.length - 1 ? "0.5px solid #E5E0D8" : "none",
                      transition: "background-color 0.2s",
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = "#F9F9F9"}
                    onMouseLeave={(e) => e.target.style.backgroundColor = "transparent"}
                  >
                    <td style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      fontFamily: "'DM Mono', monospace",
                      color: "#1F1F1F",
                    }}>
                      {c.source_currency}
                    </td>
                    <td style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      fontFamily: "'DM Mono', monospace",
                      color: "#1F1F1F",
                    }}>
                      {c.target_currency}
                    </td>
                    <td style={{
                      padding: "12px 16px",
                      textAlign: "right",
                      fontSize: "12px",
                      color: "#7A7570",
                    }}>
                      {c.max_transfer_usd
                        ? `$${c.max_transfer_usd.toLocaleString()}`
                        : "No limit"}
                    </td>
                    <td style={{
                      padding: "12px 16px",
                      textAlign: "right",
                      fontSize: "12px",
                      color: "#7A7570",
                    }}>
                      ${c.min_transfer_usd.toFixed(2)}
                    </td>
                    <td style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      color: "#7A7570",
                    }}>
                      {SETTLEMENT_LABEL(c.settlement_hours)}
                    </td>
                    <td style={{
                      padding: "12px 16px",
                      fontSize: "11px",
                    }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "4px 10px",
                          borderRadius: "4px",
                          backgroundColor:
                            c.kyc_tier_required === 2 ? "#FEF3C7" : "#E5E0D8",
                          color: c.kyc_tier_required === 2 ? "#92400E" : "#7A7570",
                          fontWeight: 500,
                        }}
                      >
                        Tier {c.kyc_tier_required}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={6}
                    style={{
                      padding: "32px 16px",
                      textAlign: "center",
                      fontSize: "13px",
                      color: "#A8A39C",
                    }}
                  >
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

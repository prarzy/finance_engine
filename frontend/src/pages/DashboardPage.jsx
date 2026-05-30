import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "just now";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function StatCard({ value, label, sub }) {
  return (
    <div style={{
      border: "0.5px solid #E5E0D8",
      borderRadius: "8px",
      padding: "20px",
      backgroundColor: "#fff",
    }}>
      <div style={{
        fontFamily: "'DM Mono', monospace",
        fontSize: "28px",
        fontWeight: 300,
        color: "#1F1F1F",
        marginBottom: "8px",
      }}>
        {value}
      </div>
      <div style={{
        fontSize: "10px",
        color: "#A8A39C",
        textTransform: "uppercase",
        letterSpacing: "0.06em",
        marginBottom: sub ? "4px" : 0,
      }}>
        {label}
      </div>
      {sub && (
        <div style={{
          fontSize: "12px",
          color: "#7A7570",
        }}>
          {sub}
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const data = await api.getDashboardSummary(token);
        setSummary(data);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      fetchDashboard();
    }
  }, [token]);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 18) return "Good afternoon";
    return "Good evening";
  };

  if (loading) {
    return (
      <div style={{ padding: "32px", textAlign: "center", color: "#A8A39C", fontSize: "13px" }}>
        Loading dashboard…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        maxWidth: "800px", 
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
          Error loading dashboard: {error}
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 40px 64px" }}>
      {/* Header with greeting and CTA */}
      <div style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        marginBottom: "48px",
      }}>
        <div>
          <h1 style={{
            fontFamily: "'Cormorant Garamond', serif",
            fontSize: "40px",
            fontWeight: 300,
            color: "#1F1F1F",
            margin: "0 0 8px 0",
          }}>
            {greeting()}.
          </h1>
          <p style={{ fontSize: "13px", color: "#A8A39C", margin: 0 }}>
            {user?.email}
          </p>
        </div>
        <Link
          to="/analyze"
          style={{
            padding: "12px 24px",
            backgroundColor: "#1F1F1F",
            color: "#fff",
            borderRadius: "8px",
            fontSize: "13px",
            fontWeight: 500,
            textDecoration: "none",
            border: "none",
            cursor: "pointer",
            transition: "background-color 0.2s",
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = "#3A3A3A"}
          onMouseLeave={(e) => e.target.style.backgroundColor = "#1F1F1F"}
        >
          Analyze Routes →
        </Link>
      </div>

      {/* Stats row */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "16px",
        marginBottom: "48px",
      }}>
        <StatCard
          value={summary?.total_analyses ?? 0}
          label="Routes analyzed"
        />
        <StatCard
          value={summary?.most_analyzed_corridor ?? "—"}
          label="Top corridor"
        />
        <StatCard
          value={`Tier ${user?.kyc_tier ?? 1}`}
          label="Account level"
          sub={user?.kyc_tier === 2 ? "Fully verified" : "Basic verified"}
        />
      </div>

      {/* Recent analyses */}
      {summary?.recent_transactions?.length > 0 && (
        <section style={{ marginBottom: "48px" }}>
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
              Recent Analyses
            </h2>
            <Link
              to="/history"
              style={{
                fontSize: "12px",
                color: "#A8A39C",
                textDecoration: "none",
                transition: "color 0.2s",
              }}
              onMouseEnter={(e) => e.target.style.color = "#1F1F1F"}
              onMouseLeave={(e) => e.target.style.color = "#A8A39C"}
            >
              View all →
            </Link>
          </div>
          <div style={{
            border: "0.5px solid #E5E0D8",
            borderRadius: "8px",
            overflow: "hidden",
            backgroundColor: "#fff",
          }}>
            {summary.recent_transactions.map((t, idx) => (
              <div
                key={t.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "16px 20px",
                  borderBottom: idx < summary.recent_transactions.length - 1 ? "0.5px solid #E5E0D8" : "none",
                  transition: "background-color 0.2s",
                  backgroundColor: "#fff",
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = "#F9F9F9"}
                onMouseLeave={(e) => e.target.style.backgroundColor = "#fff"}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
                  <span style={{
                    fontFamily: "'DM Mono', monospace",
                    fontSize: "13px",
                    color: "#1F1F1F",
                    minWidth: "80px",
                  }}>
                    {t.source} → {t.target}
                  </span>
                  <span style={{
                    fontSize: "13px",
                    color: "#7A7570",
                  }}>
                    {t.amount.toLocaleString()} {t.source}
                  </span>
                </div>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "32px",
                  fontSize: "12px",
                  color: "#A8A39C",
                }}>
                  <span>
                    {t.hop_count} {t.hop_count === 1 ? "hop" : "hops"}
                  </span>
                  <span>{timeAgo(t.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Top corridors bar chart */}
      {summary?.top_corridors?.length > 0 && (
        <section style={{ marginBottom: "48px" }}>
          <h2 style={{
            fontSize: "11px",
            color: "#A8A39C",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            margin: "0 0 16px 0",
            fontWeight: 500,
          }}>
            Most Analyzed Corridors
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {summary.top_corridors.map((c, i) => {
              const max = summary.top_corridors[0].count;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <span style={{
                    fontFamily: "'DM Mono', monospace",
                    fontSize: "13px",
                    color: "#1F1F1F",
                    minWidth: "70px",
                  }}>
                    {c.corridor}
                  </span>
                  <div style={{
                    flex: 1,
                    height: "8px",
                    backgroundColor: "#E5E0D8",
                    borderRadius: "2px",
                    overflow: "hidden",
                  }}>
                    <div
                      style={{
                        height: "100%",
                        backgroundColor: "#B0AAA2",
                        borderRadius: "2px",
                        transition: "width 0.3s ease-out",
                        width: `${(c.count / max) * 100}%`,
                      }}
                    />
                  </div>
                  <span style={{
                    fontSize: "12px",
                    color: "#A8A39C",
                    minWidth: "30px",
                    textAlign: "right",
                  }}>
                    {c.count}
                  </span>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Empty state for new users */}
      {summary?.total_analyses === 0 && (
        <div style={{
          border: "1px dashed #E5E0D8",
          borderRadius: "8px",
          padding: "40px",
          textAlign: "center",
        }}>
          <p style={{
            fontSize: "14px",
            color: "#7A7570",
            margin: "0 0 12px 0",
          }}>
            No analyses yet.
          </p>
          <p style={{
            fontSize: "12px",
            color: "#A8A39C",
            maxWidth: "480px",
            margin: "0 auto 24px",
            lineHeight: 1.6,
          }}>
            Finova models international payment corridors as a directed graph and finds the
            cheapest multi-hop route using Dijkstra's algorithm with live FX rates.
          </p>
          <Link
            to="/analyze"
            style={{
              display: "inline-block",
              padding: "12px 24px",
              border: "0.5px solid #C4BEB6",
              borderRadius: "8px",
              fontSize: "13px",
              color: "#7A7570",
              textDecoration: "none",
              transition: "all 0.2s",
              backgroundColor: "#fff",
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = "#1F1F1F";
              e.target.style.color = "#1F1F1F";
              e.target.style.backgroundColor = "#F9F9F9";
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = "#C4BEB6";
              e.target.style.color = "#7A7570";
              e.target.style.backgroundColor = "#fff";
            }}
          >
            Start analyzing →
          </Link>
        </div>
      )}
    </div>
  );
}

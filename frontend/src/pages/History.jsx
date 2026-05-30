import { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { API_BASE_URL } from "../services/api";

export default function History() {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Failed to fetch history");
        const data = await response.json();
        setTransactions(data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  if (!token) {
    return <div style={{ padding: "32px" }}>Please log in to view history.</div>;
  }

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "32px 40px 64px" }}>
      <h1 className="text-heading-1" style={{ color: "var(--color-text-primary)", marginBottom: "24px" }}>
        Transaction History
      </h1>

      {error && (
        <div
          className="mb-4 p-3 rounded-md text-sm"
          style={{
            backgroundColor: "var(--color-error-bg)",
            border: "0.5px solid var(--color-error-border)",
            color: "var(--color-error-text)",
          }}
        >
          {error}
        </div>
      )}

      {loading && <p>Loading history...</p>}

      {!loading && transactions.length === 0 && (
        <p style={{ color: "var(--color-text-secondary)" }}>No transactions yet.</p>
      )}

      {!loading && transactions.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ minWidth: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "var(--color-surface-muted)" }}>
                <th
                  style={{
                    border: `0.5px solid var(--color-border)`,
                    padding: "12px 16px",
                    textAlign: "left",
                    color: "var(--color-text-secondary)",
                    fontSize: "12px",
                  }}
                >
                  Date
                </th>
                <th
                  style={{
                    border: `0.5px solid var(--color-border)`,
                    padding: "12px 16px",
                    textAlign: "left",
                    color: "var(--color-text-secondary)",
                    fontSize: "12px",
                  }}
                >
                  Route
                </th>
                <th
                  style={{
                    border: `0.5px solid var(--color-border)`,
                    padding: "12px 16px",
                    textAlign: "left",
                    color: "var(--color-text-secondary)",
                    fontSize: "12px",
                  }}
                >
                  Amount
                </th>
                <th
                  style={{
                    border: `0.5px solid var(--color-border)`,
                    padding: "12px 16px",
                    textAlign: "left",
                    color: "var(--color-text-secondary)",
                    fontSize: "12px",
                  }}
                >
                  Cost
                </th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx, idx) => (
                <tr key={idx}>
                  <td
                    style={{
                      border: `0.5px solid var(--color-border)`,
                      padding: "12px 16px",
                      fontSize: "12px",
                    }}
                  >
                    {new Date(tx.created_at).toLocaleDateString()}
                  </td>
                  <td
                    style={{
                      border: `0.5px solid var(--color-border)`,
                      padding: "12px 16px",
                      fontSize: "12px",
                    }}
                  >
                    {tx.source_currency} → {tx.target_currency}
                  </td>
                  <td
                    style={{
                      border: `0.5px solid var(--color-border)`,
                      padding: "12px 16px",
                      fontSize: "12px",
                    }}
                  >
                    {tx.amount} {tx.source_currency}
                  </td>
                  <td
                    style={{
                      border: `0.5px solid var(--color-border)`,
                      padding: "12px 16px",
                      fontSize: "12px",
                    }}
                  >
                    ${tx.estimated_cost_usd?.toFixed(2) || "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

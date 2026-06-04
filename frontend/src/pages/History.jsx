import { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";

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
        const data = await api.getHistory(token);
        setTransactions(data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  const handleDelete = async (transactionId) => {
    if (!window.confirm("Are you sure you want to delete this history entry?")) {
      return;
    }

    try {
      await api.deleteTransaction(transactionId, token);
      setTransactions((prev) => prev.filter((tx) => tx.id !== transactionId));
    } catch (err) {
      setError(err.message || "Failed to delete transaction.");
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to delete ALL transaction history? This cannot be undone.")) {
      return;
    }

    try {
      await api.clearHistory(token);
      setTransactions([]);
    } catch (err) {
      setError(err.message || "Failed to clear transaction history.");
    }
  };

  if (!token) {
    return <div style={{ padding: "32px" }}>Please log in to view history.</div>;
  }

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "32px 40px 64px" }}>
      {/* Header section with Clear All */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <h1 className="text-heading-1" style={{ color: "var(--color-text-primary)", margin: 0 }}>
          Transaction History
        </h1>
        {transactions.length > 0 && (
          <button
            onClick={handleClearAll}
            style={{
              padding: "8px 16px",
              border: "0.5px solid var(--color-border)",
              borderRadius: "6px",
              fontSize: "12px",
              color: "#DC2626",
              cursor: "pointer",
              backgroundColor: "transparent",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = "#FEE2E2";
              e.target.style.borderColor = "#FCA5A5";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.borderColor = "var(--color-border)";
            }}
          >
            Clear All
          </button>
        )}
      </div>

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
                <th
                  style={{
                    border: `0.5px solid var(--color-border)`,
                    padding: "12px 16px",
                    textAlign: "center",
                    color: "var(--color-text-secondary)",
                    fontSize: "12px",
                    width: "80px",
                  }}
                >
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
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
                  <td
                    style={{
                      border: `0.5px solid var(--color-border)`,
                      padding: "8px 16px",
                      textAlign: "center",
                      fontSize: "12px",
                    }}
                  >
                    <button
                      onClick={() => handleDelete(tx.id)}
                      title="Delete entry"
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "var(--color-text-secondary)",
                        fontSize: "18px",
                        lineHeight: "1",
                        cursor: "pointer",
                        padding: "4px 8px",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        transition: "all 0.2s",
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.color = "#DC2626";
                        e.target.style.transform = "scale(1.2)";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.color = "var(--color-text-secondary)";
                        e.target.style.transform = "scale(1)";
                      }}
                    >
                      &times;
                    </button>
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

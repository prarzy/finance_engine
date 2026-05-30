import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import AuthPanel from "../components/AuthPanel";

export default function Dashboard() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  if (!token) {
    return <AuthPanel />;
  }

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "48px 40px 64px" }}>
      {/* Welcome Header */}
      <div style={{ marginBottom: "64px" }}>
        <h1 className="text-heading-1" style={{ color: "var(--color-text-primary)", marginBottom: "12px" }}>
          Welcome back
        </h1>
        <p style={{ color: "var(--color-text-secondary)", fontSize: "16px", lineHeight: "1.6" }}>
          Optimize your global payments with intelligent route analysis
        </p>
      </div>

      {/* Feature Cards - 3 across */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "24px", marginBottom: "48px" }}>
        {/* Analyze Routes Card */}
        <div
          style={{
            border: "0.5px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "32px",
            backgroundColor: "var(--color-surface)",
            cursor: "pointer",
            transition: "all var(--transition-base)",
          }}
          onClick={() => navigate("/analyze")}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--color-accent)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(58, 107, 74, 0.1)";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--color-border)";
            e.currentTarget.style.boxShadow = "none";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          {/* SVG Icon - Route Paths */}
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            style={{ marginBottom: "16px" }}
          >
            <path
              d="M6 24H42M36 18L42 24L36 30M6 18L12 24L6 30"
              stroke="var(--color-accent)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="24" cy="24" r="3" fill="var(--color-accent)" />
          </svg>
          <h2 className="text-heading-2" style={{ color: "var(--color-text-primary)", marginBottom: "8px", fontSize: "20px" }}>
            Analyze Routes
          </h2>
          <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
            Enter transfer details and discover optimal payment routes with the lowest fees
          </p>
        </div>

        {/* Supported Routes Card */}
        <div
          style={{
            border: "0.5px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "32px",
            backgroundColor: "var(--color-surface)",
            cursor: "pointer",
            transition: "all var(--transition-base)",
          }}
          onClick={() => navigate("/supported-routes")}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--color-accent)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(58, 107, 74, 0.1)";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--color-border)";
            e.currentTarget.style.boxShadow = "none";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          {/* SVG Icon - Globe/Network */}
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            style={{ marginBottom: "16px" }}
          >
            <circle cx="24" cy="24" r="18" stroke="var(--color-accent)" strokeWidth="2" />
            <circle cx="24" cy="24" r="12" stroke="var(--color-accent)" strokeWidth="1.5" opacity="0.5" />
            <circle cx="24" cy="24" r="6" stroke="var(--color-accent)" strokeWidth="1.5" opacity="0.5" />
            <path d="M24 6V42M6 24H42" stroke="var(--color-accent)" strokeWidth="1.5" opacity="0.5" />
            <circle cx="24" cy="24" r="3" fill="var(--color-accent)" />
          </svg>
          <h2 className="text-heading-2" style={{ color: "var(--color-text-primary)", marginBottom: "8px", fontSize: "20px" }}>
            Supported Routes
          </h2>
          <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
            Browse all payment corridors across trusted providers with transfer limits
          </p>
        </div>

        {/* Transaction History Card */}
        <div
          style={{
            border: "0.5px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "32px",
            backgroundColor: "var(--color-surface)",
            cursor: "pointer",
            transition: "all var(--transition-base)",
          }}
          onClick={() => navigate("/history")}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--color-accent)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(58, 107, 74, 0.1)";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--color-border)";
            e.currentTarget.style.boxShadow = "none";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          {/* SVG Icon - Document/Receipt */}
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            style={{ marginBottom: "16px" }}
          >
            <rect x="10" y="6" width="28" height="36" rx="2" stroke="var(--color-accent)" strokeWidth="2" />
            <line x1="14" y1="14" x2="34" y2="14" stroke="var(--color-accent)" strokeWidth="1.5" />
            <line x1="14" y1="20" x2="34" y2="20" stroke="var(--color-accent)" strokeWidth="1.5" />
            <line x1="14" y1="26" x2="28" y2="26" stroke="var(--color-accent)" strokeWidth="1.5" />
            <line x1="14" y1="32" x2="32" y2="32" stroke="var(--color-accent)" strokeWidth="1.5" />
          </svg>
          <h2 className="text-heading-2" style={{ color: "var(--color-text-primary)", marginBottom: "8px", fontSize: "20px" }}>
            Transaction History
          </h2>
          <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
            View your past transactions and payment routes used for each transfer
          </p>
        </div>
      </div>

      {/* Info Section */}
      <div
        style={{
          background: "var(--color-surface-best)",
          border: "0.5px solid var(--color-accent-border)",
          borderRadius: "var(--radius-lg)",
          padding: "40px",
          textAlign: "left",
        }}
      >
        <h2 className="text-heading-2" style={{ color: "var(--color-text-primary)", marginBottom: "16px", fontSize: "20px" }}>
          How Finova Works
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "32px" }}>
          <div>
            <div
              style={{
                width: "40px",
                height: "40px",
                background: "var(--color-accent-light)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 600,
                color: "var(--color-accent)",
                marginBottom: "12px",
              }}
            >
              1
            </div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
              <strong>Enter Details</strong> — Specify source/target currency, amount, and preferred providers
            </p>
          </div>
          <div>
            <div
              style={{
                width: "40px",
                height: "40px",
                background: "var(--color-accent-light)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 600,
                color: "var(--color-accent)",
                marginBottom: "12px",
              }}
            >
              2
            </div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
              <strong>Compare Routes</strong> — Algorithm finds optimal routes ranked by total cost
            </p>
          </div>
          <div>
            <div
              style={{
                width: "40px",
                height: "40px",
                background: "var(--color-accent-light)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 600,
                color: "var(--color-accent)",
                marginBottom: "12px",
              }}
            >
              3
            </div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "13px", lineHeight: "1.6" }}>
              <strong>Choose & Execute</strong> — Select the best route and process your payment
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import History from "./pages/History";
import SupportedRoutes from "./pages/SupportedRoutes";
import Auth from "./pages/Auth";
import { useAuth, AuthProvider } from "./hooks/useAuth";

/**
 * ProtectedRoute - Wraps routes that require authentication
 */
function ProtectedRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/auth" />;
}

function AppContent() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "var(--color-canvas)",
        color: "var(--color-text-primary)",
        fontFamily: "-apple-system,'Segoe UI',sans-serif",
      }}
    >
      <Navbar />
      <main style={{ flex: 1, backgroundColor: "var(--color-canvas)" }}>
        <Routes>
          <Route path="/auth" element={<Auth />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analyze"
            element={
              <ProtectedRoute>
                <Analyze />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            }
          />
          <Route
            path="/supported-routes"
            element={
              <ProtectedRoute>
                <SupportedRoutes />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </main>
      <footer
        style={{
          borderTop: "0.5px solid var(--color-border)",
          padding: "12px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "var(--color-surface)",
        }}
      >
        <span
          className="font-mono-custom"
          style={{ fontSize: "11px", color: "#B0AAA2" }}
        >
          Finova · rates via ExchangeRate-API
        </span>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}


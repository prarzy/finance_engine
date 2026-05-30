import { useAnalyze } from "../hooks/useAnalyze";
import { useAuth } from "../hooks/useAuth";
import PaymentForm from "../components/PaymentForm";
import ResultsPanel from "../components/ResultsPanel";
import QueryRecap from "../components/QueryRecap";
import AuthPanel from "../components/AuthPanel";

export default function Analyze() {
  const { token } = useAuth();
  const { form, updateField, loading, error, result, submit, resetResult, limitResults, limitChecking, checkTransferLimits } = useAnalyze();
  const hasResult = result !== null;

  return (
    <>
      {!token ? (
        <AuthPanel />
      ) : hasResult ? (
        <div>
          <QueryRecap form={form} result={result} onEdit={resetResult} />
          <div
            className="anim-fade-up"
            style={{ maxWidth: "860px", margin: "0 auto", padding: "32px 40px 64px" }}
          >
            <ResultsPanel result={result} form={form} />
          </div>
        </div>
      ) : (
        <div style={{ maxWidth: "480px", margin: "0 auto", padding: "36px 40px" }}>
          <PaymentForm
            form={form}
            updateField={updateField}
            loading={loading}
            error={error}
            onSubmit={() => submit(token)}
            limitResults={limitResults}
            limitChecking={limitChecking}
            onCheckLimits={checkTransferLimits}
          />
        </div>
      )}
    </>
  );
}

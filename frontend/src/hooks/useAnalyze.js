import { useState } from "react";
import { analyzePayment } from "../services/api";

/**
 * useAnalyze — custom hook (frontend_plan.md §4)
 *
 * Encapsulates form state, fetch lifecycle, and AnalyzeResponse result.
 * Exposes a `submit(token)` function that runs client-side validation
 * then calls POST /analyze and updates state according to the data flow
 * defined in frontend_plan.md §6.
 */
export function useAnalyze() {
  // Form state — mirrors AnalyzeRequest body exactly
  const [form, setForm] = useState({
    amount: "",
    source_currency: "USD",
    target_currency: "EUR",
    available_methods: null, // null = all 7 rails; array = filtered subset
  });

  // Request lifecycle
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); // string from { "error": "..." } envelope

  // API result — mirrors AnalyzeResponse exactly when populated
  const [result, setResult] = useState(null);

  // ── Helper: update a single form field and clear any stale error ──────────
  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError(null); // per plan §4: "Form field changed → error: null (clear)"
  }

  // ── Amount parser — strips commas inserted by the blur formatter ────────────
  function parseAmount(raw) {
    return Number(String(raw).replace(/,/g, ""));
  }

  // ── Client-side validation ─────────────────────────────────────────────────
  function validate() {
    const amount = parseAmount(form.amount);
    if (!form.amount || isNaN(amount) || amount <= 0) {
      return "Amount must be a number greater than 0.";
    }
    const src = form.source_currency.trim().toUpperCase();
    const tgt = form.target_currency.trim().toUpperCase();
    if (src.length !== 3 || tgt.length !== 3) {
      return "Currency codes must be exactly 3 characters.";
    }
    if (src === tgt) {
      return "Source and target currencies must be different.";
    }
    return null; // valid
  }

  // ── Submit — implements the data flow from frontend_plan.md §6 ────────────
  /**
   * @param {string|null} token  JWT from App-level auth state, or null
   */
  async function submit(token = null) {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    const body = {
      amount: parseAmount(form.amount),
      source_currency: form.source_currency.trim().toUpperCase(),
      target_currency: form.target_currency.trim().toUpperCase(),
      // Send null (backend defaults to all rails) or the filtered array
      available_methods: form.available_methods,
    };

    try {
      const data = await analyzePayment(body, token);
      setResult(data);
    } catch (err) {
      // Covers both backend error envelopes and network failures
      setError(err.message ?? "Something went wrong. Please try again.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function resetResult() {
    setResult(null);
    setError(null);
  }

  return {
    form,
    setForm,
    updateField,
    loading,
    error,
    setError,
    result,
    submit,
    resetResult,
  };
}

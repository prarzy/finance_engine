/**
 * api.js — HTTP service layer (frontend_plan.md §6)
 *
 * All fetch calls to the backend go through this module.
 * Errors are always thrown as plain Error objects with the
 * message taken from the backend { "error": "..." } envelope.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
export { BASE_URL as API_BASE_URL };

// ─── shared helper ────────────────────────────────────────────────────────────

/**
 * Build Authorization header object if a token is present.
 * @param {string|null} token
 * @returns {object}
 */
function authHeader(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Parse a response, throwing a descriptive Error on non-2xx status.
 * Reads the backend { "error": "..." } envelope when available.
 * Falls back to a generic message for network failures or unexpected shapes.
 * @param {Response} res
 * @returns {Promise<any>}
 */
async function parseResponse(res) {
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`Server returned status ${res.status} with no JSON body.`);
  }

  if (!res.ok) {
    // Backend always sends { "error": "..." } for 4xx / 5xx (see api_contract.md §5)
    const message = data?.error ?? `Request failed with status ${res.status}`;
    throw new Error(message);
  }

  return data;
}

// ─── Payment analysis ─────────────────────────────────────────────────────────

/**
 * POST /analyze
 *
 * Analyzes all payment routes for a transaction.
 * Token is optional — results are persisted only when authenticated.
 *
 * @param {{ amount: number, source_currency: string, target_currency: string, available_methods: string[]|null }} body
 * @param {string|null} token  JWT or null (unauthenticated)
 * @returns {Promise<import('../types').AnalyzeResponse>}
 */
export async function analyzePayment(body, token = null) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(token),
    },
    body: JSON.stringify(body),
  });

  return parseResponse(res);
}

/**
 * GET /recommend
 *
 * Lightweight recommendation — no auth, no persistence.
 * Returns best route + up to 3 alternatives.
 *
 * @param {{ amount: number, source_currency: string, target_currency: string }} params
 * @returns {Promise<import('../types').RecommendResponse>}
 */
export async function getRecommendation(params) {
  const qs = new URLSearchParams({
    amount: String(params.amount),
    source_currency: params.source_currency,
    target_currency: params.target_currency,
  });

  const res = await fetch(`${BASE_URL}/recommend?${qs}`);
  return parseResponse(res);
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

/**
 * POST /auth/login  (OAuth2 form data — NOT JSON)
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<import('../types').TokenOut>}
 */
export async function login(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);   // backend field name is "username" (OAuth2 spec)
  form.append("password", password);

  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  return parseResponse(res);
}

/**
 * POST /auth/register
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<import('../types').UserOut>}
 */
export async function register(email, password) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  return parseResponse(res);
}

/**
 * GET /auth/me
 *
 * @param {string} token
 * @returns {Promise<import('../types').UserOut>}
 */
export async function getMe(token) {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: authHeader(token),
  });

  return parseResponse(res);
}

/**
 * GET /history  (requires auth)
 *
 * @param {string} token
 * @param {{ page?: number, page_size?: number }} params
 * @returns {Promise<import('../types').TransactionOut[]>}
 */
export async function getHistory(token, params = {}) {
  const qs = new URLSearchParams();
  if (params.page)      qs.set("page",      String(params.page));
  if (params.page_size) qs.set("page_size", String(params.page_size));

  const res = await fetch(`${BASE_URL}/history?${qs}`, {
    headers: authHeader(token),
  });

  return parseResponse(res);
}

// ─── New constraint-based endpoints ────────────────────────────────────────────

/**
 * POST /check-limits
 *
 * Pre-validates transfer limits for a corridor WITHOUT running Dijkstra.
 * Called by frontend on amount change with debounce.
 * Returns per-provider validity for the direct corridor.
 *
 * @param {{ source_currency: string, target_currency: string, amount: number, methods: string[] }} body
 * @param {string|null} token  Optional JWT
 * @returns {Promise<{ results: Array<{provider: string, valid: boolean, error: string|null, max_transfer_usd: number|null}>, any_valid: boolean, amount_usd: number }>}
 */
export async function checkLimits(body, token = null) {
  const res = await fetch(`${BASE_URL}/check-limits`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(token),
    },
    body: JSON.stringify(body),
  });

  return parseResponse(res);
}

/**
 * GET /corridors
 *
 * Returns all supported currencies and corridors grouped by provider.
 * Used by the Supported Routes & Currencies page.
 *
 * @returns {Promise<{ currencies: Array<{code: string, name: string, symbol: string, can_hold: boolean, is_source_only: boolean}>, corridors_by_provider: {[provider_slug]: Array} }>}
 */
export async function getSupportedRoutes() {
  const res = await fetch(`${BASE_URL}/corridors`);
  return parseResponse(res);
}

/**
 * GET /dashboard/summary  (requires auth)
 *
 * Returns dashboard stats for logged-in user.
 *
 * @param {string} token
 * @returns {Promise<{ total_analyses: number, total_saved_usd: number, most_analyzed_corridor: string|null, recent_transactions: Array<{id: string, source: string, target: string, amount: number, hop_count: number, created_at: string}>, top_corridors: Array<{corridor: string, count: number}> }>}
 */
export async function getDashboardSummary(token) {
  const res = await fetch(`${BASE_URL}/dashboard/summary`, {
    headers: authHeader(token),
  });

  return parseResponse(res);
}

// ─── Namespace export ──────────────────────────────────────────────────────────
// Aggregates all API methods for convenient import: import { api } from "./api"

export const api = {
  analyzePayment,
  getRecommendation,
  login,
  register,
  getMe,
  getHistory,
  checkLimits,
  getSupportedRoutes,
  getDashboardSummary,
};

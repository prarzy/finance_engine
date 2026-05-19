/**
 * formatters.js — display utility functions (frontend_plan.md §3 / §7)
 *
 * All monetary and label formatting used across components lives here
 * so rendering logic stays out of JSX.
 */

/**
 * Format a USD float as "$X.XX"
 * @param {number} value
 * @returns {string}
 */
export function formatUSD(value) {
  return `$${Number(value).toFixed(2)}`;
}

/**
 * Format a percentage float as "X.XX%"
 * @param {number} value
 * @returns {string}
 */
export function formatPct(value) {
  return `${Number(value).toFixed(2)}%`;
}

/**
 * Convert processing_days to a human-readable label.
 * - 0  → "Instant"
 * - 1  → "1 business day"
 * - N  → "N business days"
 * @param {number} days
 * @returns {string}
 */
export function formatDays(days) {
  if (days === 0) return "Instant";
  if (days === 1) return "1 business day";
  return `${days} business days`;
}

/**
 * Convert a method_name key to a display label.
 * e.g. "bank_transfer" → "Bank Transfer"
 * @param {string} method
 * @returns {string}
 */
export function formatMethodName(method) {
  return method
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Format an ISO 8601 timestamp to "HH:MM UTC"
 * Used for the "as of ..." footnote in ResultsPanel.
 * @param {string} isoString
 * @returns {string}
 */
export function formatTimestamp(isoString) {
  const d = new Date(isoString);
  const hh = String(d.getUTCHours()).padStart(2, "0");
  const mm = String(d.getUTCMinutes()).padStart(2, "0");
  return `${hh}:${mm} UTC`;
}

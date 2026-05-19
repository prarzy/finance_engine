/**
 * routeUtils.js — helpers for parsing multi-hop route data.
 */

const SEP = "__";

/** Parse "wise__USD__EUR" → { method: "wise", src: "USD", tgt: "EUR" } */
export function parseMethodNode(node) {
  const parts = node.split(SEP);
  return { method: parts[0], src: parts[1], tgt: parts[2] };
}

export function isMethodNode(node) {
  return node.includes(SEP);
}

/** "bank_transfer" → "Bank Transfer" */
export function formatMethodName(key) {
  return (key ?? "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** "USD" → "$", "EUR" → "€", etc. */
export function currencySymbol(code) {
  const map = { USD: "$", EUR: "€", GBP: "£", INR: "₹", AED: "د.إ", JPY: "¥" };
  return map[code] ?? code;
}

/**
 * Parse raw path array into alternating [currency, method, currency, ...] segments.
 * Returns array of { type: "currency"|"method", value, label, src?, tgt? }
 */
export function parsePath(path = []) {
  return path.map((node) => {
    if (isMethodNode(node)) {
      const { method, src, tgt } = parseMethodNode(node);
      return { type: "method", value: node, label: formatMethodName(method), method, src, tgt };
    }
    return { type: "currency", value: node, label: node };
  });
}

export function fmt(n) {
  return "$" + Number(n ?? 0).toFixed(2);
}

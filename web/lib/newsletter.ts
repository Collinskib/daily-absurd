import crypto from "node:crypto";

const SECRET = process.env.NEWSLETTER_SECRET ?? "daily-absurd-dev-secret";
const REPO = process.env.NEWSLETTER_REPO ?? "";
const DISPATCH_TOKEN = process.env.NEWSLETTER_DISPATCH_TOKEN ?? "";

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) && email.length <= 254;
}

export function signEmail(email: string): string {
  return crypto.createHmac("sha256", SECRET).update(email.toLowerCase()).digest("hex").slice(0, 24);
}

export function unsubscribeUrl(base: string, email: string): string {
  const t = signEmail(email);
  return `${base}/api/newsletter?action=unsubscribe&email=${encodeURIComponent(email)}&token=${t}`;
}

/**
 * Forwards a newsletter event to the repository, which records it in
 * web/content/subscribers.ndjson via GitHub Actions. When no dispatch
 * token is configured (local dev), the event is simply accepted.
 */
export async function dispatchSubscriberEvent(
  eventType: "newsletter-signup" | "newsletter-unsubscribe",
  email: string,
): Promise<{ queued: boolean }> {
  if (!DISPATCH_TOKEN || !REPO) return { queued: false };
  const res = await fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${DISPATCH_TOKEN}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "daily-absurd-site",
    },
    body: JSON.stringify({
      event_type: eventType,
      client_payload: { email: email.toLowerCase() },
    }),
  });
  if (!res.ok) throw new Error(`dispatch failed: ${res.status}`);
  return { queued: true };
}

import { NextRequest, NextResponse } from "next/server";
import { isValidEmail, signEmail, dispatchSubscriberEvent } from "@/lib/newsletter";

export async function POST(req: NextRequest) {
  let email: string;
  try {
    const body = await req.json();
    email = String(body.email ?? "").trim();
  } catch {
    return NextResponse.json({ error: "invalid request" }, { status: 400 });
  }
  if (!isValidEmail(email)) {
    return NextResponse.json({ error: "invalid email" }, { status: 422 });
  }
  try {
    await dispatchSubscriberEvent("newsletter-signup", email);
  } catch {
    return NextResponse.json({ error: "subscription unavailable" }, { status: 502 });
  }
  return NextResponse.json({ ok: true });
}

/** GET is the one-click unsubscribe/confirm target from digest emails. */
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get("action");
  const email = (searchParams.get("email") ?? "").toLowerCase();
  const token = searchParams.get("token") ?? "";

  if (action !== "unsubscribe" || !isValidEmail(email) || token !== signEmail(email)) {
    return NextResponse.redirect(new URL("/unsubscribe?state=invalid", req.url));
  }
  try {
    await dispatchSubscriberEvent("newsletter-unsubscribe", email);
  } catch {
    return NextResponse.redirect(new URL("/unsubscribe?state=error", req.url));
  }
  return NextResponse.redirect(new URL("/unsubscribe?state=done", req.url));
}

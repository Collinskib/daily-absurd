"use client";

import { useState } from "react";

export default function NewsletterForm({ compact = false }: { compact?: boolean }) {
  const [state, setState] = useState<"idle" | "done" | "error">("idle");

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const email = new FormData(form).get("email");
    try {
      const res = await fetch("/api/newsletter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      setState(res.ok ? "done" : "error");
      if (res.ok) form.reset();
    } catch {
      setState("error");
    }
  }

  if (state === "done") {
    return (
      <p className="font-serif italic text-lg">
        Splendid. Check your inbox — a confirmation is on its way.
      </p>
    );
  }

  return (
    <form onSubmit={submit} className={compact ? "flex gap-2" : "flex flex-col sm:flex-row gap-3"}>
      <label htmlFor={compact ? "nl-c" : "nl"} className="sr-only">Email address</label>
      <input
        id={compact ? "nl-c" : "nl"}
        name="email"
        type="email"
        required
        placeholder="you@example.com"
        className="flex-1 border-2 border-ink bg-paper px-4 py-3 text-sm font-sans placeholder:text-faded focus:outline-none focus:border-vermilion"
      />
      <button
        type="submit"
        className="border-2 border-ink bg-ink text-paper px-6 py-3 kicker hover:bg-vermilion hover:border-vermilion transition-colors"
      >
        Subscribe
      </button>
      {state === "error" && (
        <p className="text-vermilion text-xs mt-1">Something went sideways. Try again.</p>
      )}
    </form>
  );
}

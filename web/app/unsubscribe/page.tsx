import Link from "next/link";

export const metadata = { title: "Unsubscribe" };

const MESSAGES: Record<string, { title: string; body: string }> = {
  done: {
    title: "You're out. We'll miss you. Briefly.",
    body: "Your address has been removed from The Absurd Dispatch. The fake news will continue without you.",
  },
  invalid: {
    title: "That link didn't check out.",
    body: "The unsubscribe link was invalid or already used. If you're still receiving emails, contact desk@dailyabsurd.news.",
  },
  error: {
    title: "Something went sideways.",
    body: "We couldn't process that unsubscribe. Try again or email desk@dailyabsurd.news and we'll remove you manually.",
  },
};

export default async function Unsubscribe({
  searchParams,
}: {
  searchParams: Promise<{ state?: string }>;
}) {
  const { state } = await searchParams;
  const m = MESSAGES[state ?? "invalid"] ?? MESSAGES.invalid;
  return (
    <div className="mx-auto max-w-2xl px-6 py-24 text-center">
      <p className="satire-badge inline-block">Unsubscribe</p>
      <h1 className="font-serif font-black text-3xl sm:text-4xl mt-6">{m.title}</h1>
      <p className="mt-4 font-serif italic text-lg text-ink-soft">{m.body}</p>
      <Link href="/" className="mt-8 inline-block border-2 border-ink px-6 py-3 kicker hover:bg-ink hover:text-paper transition-colors">
        Back to the front page
      </Link>
    </div>
  );
}

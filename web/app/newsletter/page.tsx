import NewsletterForm from "@/components/NewsletterForm";

export const metadata = { title: "The Absurd Dispatch — Newsletter" };

export default function NewsletterPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-12">
      <p className="kicker text-vermilion">The Absurd Dispatch</p>
      <h1 className="font-serif font-black text-4xl sm:text-5xl mt-2 leading-tight">
        Fake news you can actually rely on.
      </h1>
      <p className="mt-6 font-serif italic text-xl text-ink-soft leading-relaxed">
        Every morning, one email: our best satirical stories, a joke you can
        steal for work, and absolutely nothing true enough to ruin your day.
      </p>
      <ul className="mt-8 space-y-3 font-serif text-lg text-ink-soft">
        <li>◆ The day&apos;s sharpest fabricated headlines</li>
        <li>◆ International nonsense, not just one country&apos;s</li>
        <li>◆ Unsubscribe in one click — no guilt trip, no “are you sure?”</li>
      </ul>
      <div className="mt-10 border-2 border-ink p-6 sm:p-8 bg-paper-dim">
        <NewsletterForm />
        <p className="mt-3 text-[0.65rem] uppercase tracking-widest text-faded">
          We only email subscribers. Consent is real even if the news isn&apos;t.
        </p>
      </div>
    </div>
  );
}

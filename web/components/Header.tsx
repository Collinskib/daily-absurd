import Link from "next/link";
import { site } from "@/lib/site";
import { categories, getAllArticles } from "@/lib/articles";
import Ticker from "@/components/Ticker";

export default function Header() {
  const latest = getAllArticles()
    .slice(0, 8)
    .map((a) => a.headline);
  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header className="border-b border-ink">
      <Ticker items={latest} />
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex items-end justify-between gap-4 pt-5 pb-1">
          <p className="kicker hidden sm:block text-faded">{today}</p>
          <p className="kicker text-vermilion">Est. 2026 · No. 001 · Price: Free-ish</p>
        </div>
        <Link href="/" className="block text-center py-2" aria-label={site.name}>
          <h1 className="font-serif font-black leading-none tracking-tight text-[clamp(2.6rem,8vw,5.5rem)]">
            The Daily <span className="italic text-vermilion">Absurd</span>
          </h1>
          <p className="mt-1 font-serif italic text-faded text-sm sm:text-base">
            {site.tagline}
          </p>
        </Link>
        <nav aria-label="Sections" className="rule-double mt-3 mb-1">
          <ul className="flex flex-wrap justify-center gap-x-5 gap-y-1 py-1">
            <li>
              <Link href="/" className="kicker text-ink hover:text-vermilion transition-colors">
                Front Page
              </Link>
            </li>
            {categories.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/category/${c.slug}`}
                  className="kicker text-ink-soft hover:text-vermilion transition-colors"
                >
                  {c.name}
                </Link>
              </li>
            ))}
            <li>
              <Link href="/newsletter" className="kicker text-vermilion hover:text-vermilion-deep transition-colors">
                Newsletter
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

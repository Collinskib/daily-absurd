import Link from "next/link";
import { site } from "@/lib/site";
import { categories } from "@/lib/articles";

export default function Footer() {
  return (
    <footer className="mt-16 border-t-4 border-ink bg-paper-dim">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 py-10">
        <div className="grid gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <p className="font-serif font-black text-3xl">
              The Daily <span className="italic text-vermilion">Absurd</span>
            </p>
            <p className="mt-3 max-w-md text-sm text-ink-soft leading-relaxed">
              {site.description} Nothing published here is true, except the bits
              that feel uncomfortably familiar.
            </p>
            <p className="mt-4 inline-block satire-badge">100% Fictional</p>
          </div>
          <nav aria-label="Sections">
            <p className="kicker text-faded mb-3">Sections</p>
            <ul className="grid grid-cols-1 gap-1.5 text-sm">
              {categories.slice(0, 6).map((c) => (
                <li key={c.slug}>
                  <Link href={`/category/${c.slug}`} className="text-ink-soft hover:text-vermilion transition-colors">
                    {c.name}
                  </Link>
                </li>
              ))}
              <li>
                <Link href="/category" className="text-ink font-semibold hover:text-vermilion transition-colors">
                  All sections →
                </Link>
              </li>
            </ul>
          </nav>
          <nav aria-label="About">
            <p className="kicker text-faded mb-3">The Paper</p>
            <ul className="grid grid-cols-1 gap-1.5 text-sm">
              <li><Link href="/about" className="text-ink-soft hover:text-vermilion transition-colors">About us</Link></li>
              <li><Link href="/editorial-policy" className="text-ink-soft hover:text-vermilion transition-colors">Editorial policy</Link></li>
              <li><Link href="/disclaimer" className="text-ink-soft hover:text-vermilion transition-colors">Satire disclaimer</Link></li>
              <li><Link href="/contact" className="text-ink-soft hover:text-vermilion transition-colors">Contact</Link></li>
              <li><Link href="/privacy" className="text-ink-soft hover:text-vermilion transition-colors">Privacy</Link></li>
              <li><Link href="/terms" className="text-ink-soft hover:text-vermilion transition-colors">Terms</Link></li>
              <li><a href="/feed.xml" className="text-ink-soft hover:text-vermilion transition-colors">RSS feed</a></li>
            </ul>
          </nav>
        </div>
        <div className="rule-thin mt-10 pt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-faded">
            © {new Date().getFullYear()} {site.name}. Fictional news for a factual world.
          </p>
          <div className="flex gap-4 text-xs font-semibold uppercase tracking-widest">
            <a href={site.social.x} className="text-faded hover:text-vermilion transition-colors">X</a>
            <a href={site.social.facebook} className="text-faded hover:text-vermilion transition-colors">Facebook</a>
            <a href={site.social.instagram} className="text-faded hover:text-vermilion transition-colors">Instagram</a>
            <a href={site.social.youtube} className="text-faded hover:text-vermilion transition-colors">YouTube</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

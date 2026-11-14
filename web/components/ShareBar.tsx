import { site } from "@/lib/site";

export default function ShareBar({ slug, headline }: { slug: string; headline: string }) {
  const url = encodeURIComponent(`${site.url}/articles/${slug}`);
  const text = encodeURIComponent(`${headline} — via The Daily Absurd (satire)`);
  const links = [
    { name: "X", href: `https://twitter.com/intent/tweet?text=${text}&url=${url}` },
    { name: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${url}` },
    { name: "LinkedIn", href: `https://www.linkedin.com/sharing/share-offsite/?url=${url}` },
    { name: "WhatsApp", href: `https://wa.me/?text=${text}%20${url}` },
  ];
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="kicker text-faded mr-1">Share the lie:</span>
      {links.map((l) => (
        <a
          key={l.name}
          href={l.href}
          target="_blank"
          rel="noopener noreferrer"
          className="border border-ink px-3 py-1.5 text-[0.7rem] font-bold uppercase tracking-widest hover:bg-ink hover:text-paper transition-colors"
        >
          {l.name}
        </a>
      ))}
    </div>
  );
}

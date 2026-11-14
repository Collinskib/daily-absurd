import Link from "next/link";
import { categories, getArticlesByCategory } from "@/lib/articles";

export const metadata = { title: "All Sections" };

export default function CategoryIndex() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-10">
      <h1 className="font-serif font-black text-4xl sm:text-5xl border-b-4 border-ink pb-6 mb-8">
        Every Department of Nonsense
      </h1>
      <div className="grid gap-px bg-ink/15 border border-ink/15 sm:grid-cols-2">
        {categories.map((c) => {
          const n = getArticlesByCategory(c.slug).length;
          return (
            <Link
              key={c.slug}
              href={`/category/${c.slug}`}
              className="bg-paper p-8 hover:bg-ink hover:text-paper transition-colors group"
            >
              <div className="flex items-baseline justify-between">
                <h2 className="font-serif font-bold text-2xl group-hover:text-vermilion">{c.name}</h2>
                <span className="kicker text-faded">{n} {n === 1 ? "story" : "stories"}</span>
              </div>
              <p className="mt-3 text-sm text-faded group-hover:text-paper/70 leading-relaxed">{c.blurb}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

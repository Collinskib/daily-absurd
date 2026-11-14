import Link from "next/link";
import { searchArticles, categoryName } from "@/lib/articles";
import { formatDate } from "@/lib/format";

export const metadata = { title: "Search" };

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const query = q ?? "";
  const results = searchArticles(query);

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-10">
      <h1 className="font-serif font-black text-4xl border-b-4 border-ink pb-6 mb-8">
        Search the Fiction
      </h1>
      <form method="get" action="/search" className="flex gap-3 mb-10">
        <label htmlFor="q" className="sr-only">Search</label>
        <input
          id="q"
          name="q"
          type="search"
          defaultValue={query}
          placeholder="Search our completely made-up archive…"
          className="flex-1 border-2 border-ink bg-paper px-4 py-3 text-sm focus:outline-none focus:border-vermilion"
        />
        <button type="submit" className="border-2 border-ink bg-ink text-paper px-6 kicker hover:bg-vermilion hover:border-vermilion transition-colors">
          Search
        </button>
      </form>
      {query && (
        <p className="kicker text-faded mb-6">
          {results.length} result{results.length === 1 ? "" : "s"} for “{query}”
        </p>
      )}
      <ul className="divide-y divide-ink/15">
        {results.map((a) => (
          <li key={a.slug} className="py-5">
            <Link href={`/articles/${a.slug}`}>
              <p className="kicker text-vermilion text-[0.6rem]">{categoryName(a.category)}</p>
              <h2 className="headline-md text-xl mt-1 hover-headline">{a.headline}</h2>
              <p className="mt-1 text-sm text-faded">{formatDate(a.publishedAt)}</p>
            </Link>
          </li>
        ))}
      </ul>
      {query && results.length === 0 && (
        <p className="font-serif italic text-xl text-faded py-10 text-center">
          Nothing found. Which is still more truth than we usually print.
        </p>
      )}
    </div>
  );
}

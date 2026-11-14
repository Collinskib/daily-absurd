import Link from "next/link";
import { getAllArticles, getFeatured, getArticlesByCategory, categories, categoryName } from "@/lib/articles";
import { formatDate } from "@/lib/format";
import ArticleCard from "@/components/ArticleCard";
import NewsletterForm from "@/components/NewsletterForm";

export default function Home() {
  const featured = getFeatured();
  const all = getAllArticles();
  const rest = all.filter((a) => a.slug !== featured?.slug);
  const latest = rest.slice(0, 6);
  const popular = rest.slice(0, 4);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6">
      {featured ? (
        <>
          {/* ===== FRONT PAGE ===== */}
          <section className="grid gap-8 py-10 lg:grid-cols-12">
            <div className="lg:col-span-8 reveal">
              <p className="kicker text-vermilion mb-3">Today&apos;s Absurdity</p>
              <Link href={`/articles/${featured.slug}`} className="group block">
                <h2 className="headline-xl text-[clamp(2.2rem,5.2vw,4.3rem)] group-hover:text-vermilion transition-colors">
                  {featured.headline}
                </h2>
                <p className="mt-4 font-serif italic text-xl sm:text-2xl text-ink-soft leading-snug max-w-3xl">
                  {featured.subheadline}
                </p>
                <p className="mt-4 kicker text-faded">
                  {categoryName(featured.category)} · {featured.author} · {formatDate(featured.publishedAt)}
                </p>
                {featured.art && (
                  <div className="mt-6 border-2 border-ink card-lift">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`/art/${featured.art}`} alt="" className="w-full aspect-[16/8] object-cover" />
                  </div>
                )}
              </Link>
            </div>

            <aside className="lg:col-span-4 lg:border-l lg:border-ink lg:pl-8">
              <p className="kicker text-faded rule-thick pt-2">Also Fabricated</p>
              <ul className="mt-4 divide-y divide-ink/15">
                {popular.map((a, i) => (
                  <li key={a.slug} className="py-3 reveal" style={{ "--reveal-delay": `${i * 60}ms` } as React.CSSProperties}>
                    <Link href={`/articles/${a.slug}`} className="block">
                      <p className="kicker text-vermilion text-[0.6rem]">{categoryName(a.category)}</p>
                      <h3 className="headline-md text-lg mt-1 hover-headline">{a.headline}</h3>
                    </Link>
                  </li>
                ))}
              </ul>
            </aside>
          </section>

          {/* ===== LATEST ===== */}
          <section className="rule-thick pt-6 pb-10">
            <div className="flex items-baseline justify-between mb-6">
              <h2 className="font-serif font-black text-3xl">Fresh Off the Presses</h2>
              <span className="kicker text-faded">All of it invented</span>
            </div>
            <div className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
              {latest.map((a, i) => (
                <ArticleCard key={a.slug} article={a} delay={i * 70} />
              ))}
            </div>
          </section>
        </>
      ) : (
        <section className="py-24 text-center">
          <p className="satire-badge inline-block">First edition in the works</p>
          <h2 className="headline-xl text-4xl mt-6">The presses are warming up.</h2>
          <p className="mt-4 font-serif italic text-xl text-ink-soft">
            Our reporters are out fabricating the news as we speak.
          </p>
        </section>
      )}

      {/* ===== SECTIONS ===== */}
      <section className="rule-thick pt-6 pb-10">
        <h2 className="font-serif font-black text-3xl mb-6">Departments of Nonsense</h2>
        <div className="grid gap-px bg-ink/15 border border-ink/15 sm:grid-cols-2 lg:grid-cols-5">
          {categories.map((c) => {
            return (
              <Link
                key={c.slug}
                href={`/category/${c.slug}`}
                className="bg-paper p-5 hover:bg-ink hover:text-paper transition-colors group"
              >
                <h3 className="font-serif font-bold text-lg leading-tight group-hover:text-vermilion">
                  {c.name}
                </h3>
                <p className="mt-2 text-xs leading-relaxed text-faded group-hover:text-paper/70">
                  {c.blurb}
                </p>
              </Link>
            );
          })}
        </div>
      </section>

      {/* ===== NEWSLETTER ===== */}
      <section className="my-10 border-2 border-ink bg-ink text-paper p-8 sm:p-12 relative overflow-hidden">
        <div className="absolute -right-6 -top-10 font-serif font-black text-[10rem] leading-none text-paper/5 select-none" aria-hidden="true">
          A!
        </div>
        <div className="relative max-w-2xl">
          <p className="kicker text-vermilion">The Absurd Dispatch</p>
          <h2 className="font-serif font-black text-3xl sm:text-4xl mt-3 leading-tight">
            One email a day. Zero percent true. One hundred percent read.
          </h2>
          <p className="mt-4 font-serif italic text-paper/70 text-lg">
            The finest fictional journalism delivered to your inbox before
            breakfast, in time to ruin it.
          </p>
          <div className="mt-6 max-w-lg">
            <NewsletterForm />
            <p className="mt-3 text-[0.65rem] uppercase tracking-widest text-paper/50">
              Fictional news, real consent. Unsubscribe anytime.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

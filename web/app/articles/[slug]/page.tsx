import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllArticles, getArticle, getRelated, categoryName } from "@/lib/articles";
import { site } from "@/lib/site";
import { formatDate } from "@/lib/format";
import Markdown from "@/components/Markdown";
import ArticleCard from "@/components/ArticleCard";
import ShareBar from "@/components/ShareBar";
import NewsletterForm from "@/components/NewsletterForm";

export function generateStaticParams() {
  return getAllArticles().map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const a = getArticle(slug);
  if (!a) return {};
  const url = `${site.url}/articles/${a.slug}`;
  return {
    title: a.seoTitle || a.headline,
    description: a.seoDescription || a.subheadline,
    alternates: { canonical: url },
    openGraph: {
      type: "article",
      title: a.headline,
      description: a.subheadline,
      publishedTime: a.publishedAt,
      authors: [a.author],
      tags: a.tags,
      url,
    },
    twitter: { card: "summary_large_image", title: a.headline, description: a.subheadline },
  };
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const article = getArticle(slug);
  if (!article) notFound();
  const related = getRelated(article);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SatiricalArticle",
    headline: article.headline,
    alternativeHeadline: article.subheadline,
    datePublished: article.publishedAt,
    author: { "@type": "Organization", name: article.author },
    publisher: {
      "@type": "Organization",
      name: site.name,
      url: site.url,
    },
    isAccessibleForFree: true,
    description: article.seoDescription || article.subheadline,
    mainEntityOfPage: `${site.url}/articles/${article.slug}`,
    about: article.sourceEvent,
  };

  return (
    <article className="mx-auto max-w-4xl px-4 sm:px-6 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav className="flex items-center justify-between flex-wrap gap-3">
        <Link
          href={`/category/${article.category}`}
          className="kicker text-vermilion hover:text-vermilion-deep"
        >
          {categoryName(article.category)}
        </Link>
        <span className="satire-badge">Satire · Not real news</span>
      </nav>

      <h1 className="headline-xl text-[clamp(2rem,5vw,3.6rem)] mt-5">{article.headline}</h1>
      <p className="mt-4 font-serif italic text-xl text-ink-soft leading-snug">
        {article.subheadline}
      </p>

      <div className="rule-double mt-6 py-2 flex flex-wrap items-center justify-between gap-3">
        <p className="kicker text-faded">
          By <span className="text-ink">{article.author}</span> · {formatDate(article.publishedAt)}
        </p>
        <p className="kicker text-faded">
          Inspired by actual events ·{" "}
          <span className="italic normal-case font-serif text-sm">
            {article.sourceEvent}
          </span>
        </p>
      </div>

      {article.art && (
        <figure className="mt-8">
          <div className="border-2 border-ink">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={`/art/${article.art}`} alt={`Illustration for: ${article.headline}`} className="w-full" />
          </div>
          <figcaption className="mt-2 text-xs text-faded italic">
            Artist&apos;s impression. Nothing pictured happened, is happening, or will happen.
          </figcaption>
        </figure>
      )}

      <div className="mt-8 reveal">
        <Markdown>{article.body}</Markdown>
      </div>

      <div className="mt-10 rule-thin pt-5">
        <ShareBar slug={article.slug} headline={article.headline} />
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {article.tags.map((t) => (
          <Link
            key={t}
            href={`/search?q=${encodeURIComponent(t)}`}
            className="border border-ink/30 px-2.5 py-1 text-xs text-faded hover:border-vermilion hover:text-vermilion transition-colors"
          >
            #{t}
          </Link>
        ))}
      </div>

      <aside className="mt-10 border-2 border-ink bg-paper-dim p-6">
        <p className="kicker text-vermilion">More nonsense in your inbox</p>
        <div className="mt-3 max-w-md">
          <NewsletterForm compact />
        </div>
      </aside>

      <section className="mt-12 rule-thick pt-6">
        <h2 className="font-serif font-black text-2xl mb-6">Related Fabrications</h2>
        <div className="grid gap-x-8 gap-y-8 sm:grid-cols-3">
          {related.map((a) => (
            <ArticleCard key={a.slug} article={a} />
          ))}
        </div>
      </section>
    </article>
  );
}

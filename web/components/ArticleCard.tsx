import Link from "next/link";
import type { Article } from "@/lib/articles";
import { categoryName } from "@/lib/articles";
import { formatDate } from "@/lib/format";

export default function ArticleCard({
  article,
  delay = 0,
}: {
  article: Article;
  delay?: number;
}) {
  return (
    <article className="reveal group" style={{ "--reveal-delay": `${delay}ms` } as React.CSSProperties}>
      <Link href={`/articles/${article.slug}`} className="block">
        {article.art && (
          <div className="overflow-hidden border border-ink card-lift bg-paper-dim">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`/art/${article.art}`}
              alt=""
              className="w-full aspect-[16/9] object-cover"
              loading="lazy"
            />
          </div>
        )}
        <p className="kicker text-vermilion mt-3">{categoryName(article.category)}</p>
        <h3 className="headline-md text-xl mt-1 hover-headline">{article.headline}</h3>
        <p className="mt-1.5 text-sm text-ink-soft font-serif italic leading-snug line-clamp-2">
          {article.subheadline}
        </p>
        <p className="mt-2 text-[0.7rem] uppercase tracking-widest text-faded font-sans font-semibold">
          {article.author} · {formatDate(article.publishedAt)}
        </p>
      </Link>
    </article>
  );
}

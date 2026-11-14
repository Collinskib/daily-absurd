import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { categories, getCategory, getArticlesByCategory } from "@/lib/articles";
import ArticleCard from "@/components/ArticleCard";

export function generateStaticParams() {
  return categories.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const c = getCategory(slug);
  if (!c) return {};
  return { title: c.name, description: c.blurb, alternates: { canonical: `/category/${slug}` } };
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const cat = getCategory(slug);
  if (!cat) notFound();
  const articles = getArticlesByCategory(slug);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-10">
      <header className="border-b-4 border-ink pb-6 mb-8">
        <p className="kicker text-vermilion">Department of Nonsense</p>
        <h1 className="font-serif font-black text-4xl sm:text-5xl mt-2">{cat.name}</h1>
        <p className="mt-2 font-serif italic text-lg text-ink-soft">{cat.blurb}</p>
      </header>
      {articles.length === 0 ? (
        <p className="font-serif italic text-xl text-faded py-16 text-center">
          Nothing fabricated here yet. Our writers are working on it.
        </p>
      ) : (
        <div className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((a, i) => (
            <ArticleCard key={a.slug} article={a} delay={i * 60} />
          ))}
        </div>
      )}
    </div>
  );
}

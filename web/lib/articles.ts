import fs from "node:fs";
import path from "node:path";
import categoriesJson from "@/content/categories.json";

export interface Category {
  slug: string;
  name: string;
  blurb: string;
  order: number;
}

export interface ArticleMeta {
  slug: string;
  headline: string;
  subheadline: string;
  category: string;
  author: string;
  publishedAt: string; // ISO date
  tags: string[];
  seoTitle: string;
  seoDescription: string;
  sourceEvent: string;
  sourceUrl?: string;
  featured?: boolean;
  art?: string; // path under /public/art, e.g. "my-slug.svg"
}

export interface Article extends ArticleMeta {
  body: string; // markdown
}

const ARTICLES_DIR = path.join(process.cwd(), "content", "articles");

export const categories: Category[] = (categoriesJson as Category[]).sort(
  (a, b) => a.order - b.order,
);

export function getCategory(slug: string): Category | undefined {
  return categories.find((c) => c.slug === slug);
}

export function categoryName(slug: string): string {
  return getCategory(slug)?.name ?? slug;
}

function readArticleFile(file: string): Article | null {
  try {
    const raw = fs.readFileSync(path.join(ARTICLES_DIR, file), "utf8");
    const data = JSON.parse(raw) as Article;
    if (!data.slug || !data.headline || !data.body || !data.publishedAt) return null;
    if (!getCategory(data.category)) return null;
    return data;
  } catch {
    return null;
  }
}

export function publishedTime(a: ArticleMeta): number {
  const t = Date.parse(a.publishedAt);
  return Number.isNaN(t) ? 0 : t;
}

export function getAllArticles(): Article[] {
  if (!fs.existsSync(ARTICLES_DIR)) return [];
  return fs
    .readdirSync(ARTICLES_DIR)
    .filter((f) => f.endsWith(".json"))
    .map(readArticleFile)
    .filter((a): a is Article => a !== null)
    .sort((a, b) => publishedTime(b) - publishedTime(a));
}

export function getArticle(slug: string): Article | undefined {
  return getAllArticles().find((a) => a.slug === slug);
}

export function getArticlesByCategory(slug: string): Article[] {
  return getAllArticles().filter((a) => a.category === slug);
}

export function getRelated(article: Article, limit = 3): Article[] {
  const all = getAllArticles().filter((a) => a.slug !== article.slug);
  const sameCat = all.filter((a) => a.category === article.category);
  const rest = all.filter((a) => a.category !== article.category);
  return [...sameCat, ...rest].slice(0, limit);
}

const FEATURED_FRESH_MS = 48 * 3600 * 1000;

export function getFeatured(): Article | undefined {
  const all = getAllArticles();
  const newest = all[0];
  if (!newest) return undefined;
  // A featured pin only counts while the story is fresh — it must never
  // hold the hero slot once newer stories have been out for 48h.
  const feat = all.find((a) => a.featured);
  if (feat && publishedTime(newest) - publishedTime(feat) <= FEATURED_FRESH_MS) {
    return feat;
  }
  return newest;
}

export function getAllTags(): string[] {
  const tags = new Set<string>();
  for (const a of getAllArticles()) a.tags.forEach((t) => tags.add(t));
  return [...tags].sort();
}

export function searchArticles(query: string): Article[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const words = q.split(/\s+/);
  return getAllArticles()
    .map((a) => {
      const hay = `${a.headline} ${a.subheadline} ${a.body} ${a.tags.join(" ")}`.toLowerCase();
      const score = words.reduce((s, w) => s + (hay.includes(w) ? 1 : 0), 0);
      return { a, score };
    })
    .filter((r) => r.score > 0)
    .sort((x, y) => y.score - x.score)
    .map((r) => r.a);
}

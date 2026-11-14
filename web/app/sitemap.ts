import type { MetadataRoute } from "next";
import { site } from "@/lib/site";
import { getAllArticles, categories } from "@/lib/articles";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages = [
    "",
    "/about",
    "/editorial-policy",
    "/disclaimer",
    "/contact",
    "/privacy",
    "/terms",
    "/newsletter",
    "/category",
    "/search",
  ].map((p) => ({
    url: `${site.url}${p}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: p === "" ? 1 : 0.6,
  }));

  const catPages = categories.map((c) => ({
    url: `${site.url}/category/${c.slug}`,
    lastModified: new Date(),
    changeFrequency: "daily" as const,
    priority: 0.7,
  }));

  const articlePages = getAllArticles().map((a) => ({
    url: `${site.url}/articles/${a.slug}`,
    lastModified: new Date(a.publishedAt),
    changeFrequency: "monthly" as const,
    priority: 0.9,
  }));

  return [...staticPages, ...catPages, ...articlePages];
}

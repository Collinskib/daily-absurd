import { site } from "@/lib/site";
import { getAllArticles, categoryName } from "@/lib/articles";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function buildRss(): string {
  const articles = getAllArticles().slice(0, 50);
  const items = articles
    .map(
      (a) => `    <item>
      <title>${esc(a.headline)}</title>
      <link>${site.url}/articles/${a.slug}</link>
      <guid isPermaLink="true">${site.url}/articles/${a.slug}</guid>
      <pubDate>${new Date(a.publishedAt).toUTCString()}</pubDate>
      <category>${esc(categoryName(a.category))}</category>
      <description>${esc(a.subheadline)}</description>
    </item>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${esc(site.name)}</title>
    <link>${site.url}</link>
    <description>${esc(site.description)}</description>
    <language>en</language>
    <atom:link href="${site.url}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${items}
  </channel>
</rss>`;
}

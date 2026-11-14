import { describe, it, expect } from "vitest";
import {
  getAllArticles, getArticle, categories, searchArticles,
  getRelated, categoryName, getArticlesByCategory,
} from "./articles";

describe("content model", () => {
  it("loads articles newest-first", () => {
    const all = getAllArticles();
    expect(all.length).toBeGreaterThanOrEqual(5);
    for (let i = 1; i < all.length; i++) {
      expect(all[i - 1].publishedAt >= all[i].publishedAt).toBe(true);
    }
  });

  it("every article references a valid category and required fields", () => {
    const slugs = new Set(categories.map((c) => c.slug));
    for (const a of getAllArticles()) {
      expect(slugs.has(a.category), `${a.slug} category`).toBe(true);
      expect(a.headline.length).toBeGreaterThan(10);
      expect(a.body.length).toBeGreaterThan(500);
      expect(a.sourceEvent.length).toBeGreaterThan(10);
      expect(a.seoDescription.toLowerCase()).toContain("satire");
      expect(a.tags.length).toBeGreaterThanOrEqual(3);
    }
  });

  it("slugs are unique", () => {
    const slugs = getAllArticles().map((a) => a.slug);
    expect(new Set(slugs).size).toBe(slugs.length);
  });

  it("search finds relevant articles", () => {
    const res = searchArticles("microsoft");
    expect(res.length).toBeGreaterThan(0);
    expect(res[0].headline.toLowerCase()).toContain("microsoft");
  });

  it("related articles exclude self", () => {
    const a = getAllArticles()[0];
    const rel = getRelated(a);
    expect(rel.every((r) => r.slug !== a.slug)).toBe(true);
  });

  it("category filtering works", () => {
    const cat = getAllArticles()[0].category;
    for (const a of getArticlesByCategory(cat)) {
      expect(a.category).toBe(cat);
    }
    expect(categoryName(cat)).toBeTruthy();
  });

  it("getArticle round-trips", () => {
    const a = getAllArticles()[0];
    expect(getArticle(a.slug)?.headline).toBe(a.headline);
  });
});

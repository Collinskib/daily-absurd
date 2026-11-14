import { describe, it, expect } from "vitest";
import { buildRss } from "./rss";

describe("rss", () => {
  it("builds a valid rss feed with items", () => {
    const rss = buildRss();
    expect(rss).toContain("<rss");
    expect(rss).toContain("<item>");
    expect(rss).toContain("The Daily Absurd");
    expect(rss).toContain("/articles/");
  });

  it("escapes special characters", () => {
    const rss = buildRss();
    expect(rss).not.toMatch(/&(?!amp;|lt;|gt;|quot;|apos;)[a-z]/);
  });
});

import PageShell from "@/components/PageShell";

export const metadata = { title: "Terms of Use" };

export default function Terms() {
  return (
    <PageShell kicker="The Other Boring Necessary Page" title="Terms of Use">
      <h2>The short version</h2>
      <p>
        Read, laugh, share. Do not republish our articles as your own, do not
        present them as real news, and do not use the site for anything
        unlawful.
      </p>
      <h2>Content</h2>
      <p>
        All articles are original fictional satire owned by The Daily Absurd.
        You may share links and short excerpts with attribution. Wholesale
        republication requires permission.
      </p>
      <h2>No warranty</h2>
      <p>
        The site is provided as-is. We warrant only that the news is fake. Any
        accuracy beyond the stated real-world inspiration is accidental and
        frankly embarrassing for reality.
      </p>
      <h2>Changes</h2>
      <p>
        We may update these terms. The current version is always on this page.
      </p>
    </PageShell>
  );
}

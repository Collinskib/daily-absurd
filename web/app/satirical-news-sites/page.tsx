import type { Metadata } from "next";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Satirical News Sites: 10 Sites Like The Onion",
  description:
    "A reading list of the best satirical news sites and sites like The Onion — from Reductress to the Betoota Advocate — plus how satire differs from fake news.",
  alternates: { canonical: `${site.url}/satirical-news-sites` },
};

const sites = [
  {
    name: "The Onion",
    url: "https://theonion.com",
    note: "The benchmark since 1988. America's finest news source, by its own entirely accurate description. If a headline has ever made you snort coffee, it was probably theirs.",
  },
  {
    name: "Reductress",
    url: "https://reductress.com",
    note: "Women's magazine satire with a blade hidden in the frosting. Takes the actual conventions of lifestyle media and files them to a point.",
  },
  {
    name: "The Babylon Bee",
    url: "https://babylonbee.com",
    note: "Conservative-leaning satire aimed at American politics and church culture. You will know within one headline whether it is for you.",
  },
  {
    name: "Waterford Whispers News",
    url: "https://waterfordwhispersnews.com",
    note: "Ireland's sharpest fake broadsheet. Covers Irish absurdity and world absurdity with the same straight face.",
  },
  {
    name: "NewsBiscuit",
    url: "https://newsbiscuit.com",
    note: "British satire written largely by its readers. Dry, parliamentary, and disproportionately concerned with local councils.",
  },
  {
    name: "The Beaverton",
    url: "https://thebeaverton.com",
    note: "Canada's satirical news institution, which is a real sentence. Maple- flavoured despair, impeccably reported.",
  },
  {
    name: "The Betoota Advocate",
    url: "https://www.betootaadvocate.com",
    note: "Australia's oldest and most trusted newspaper, published from an outback town that may or may not forgive us for that description.",
  },
  {
    name: "Hard Drive",
    url: "https://hard-drive.net",
    note: "Video game satire. The only publication brave enough to report that a gamer has done something normal.",
  },
  {
    name: "Duffel Blog",
    url: "https://www.duffelblog.com",
    note: "The American military's satirical news service. If you have never served, half of it is still funny. If you have, all of it is alarming.",
  },
  {
    name: "Private Eye",
    url: "https://www.private-eye.co.uk",
    note: "The UK's fortnightly institution — half satire, half genuinely investigative journalism, which is cheating but they have earned it.",
  },
  {
    name: "The Daily Absurd",
    url: "https://daily-absurd.vercel.app",
    note: "That's us. International satirical news, published twice daily by an autonomous newsroom that never sleeps and never invoices. We included ourselves because this is our website and it seemed efficient.",
  },
];

export default function SatiricalNewsSites() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Satirical news sites worth reading",
    itemListElement: sites.map((s, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: s.name,
      url: s.url,
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageShell
        kicker="A Public Service"
        title="The Best Satirical News Sites, Ranked by a Publication That Is Definitely Impartial"
      >
        <p>
          Looking for <strong>satirical news sites</strong> or{" "}
          <strong>sites like The Onion</strong>? Good instinct. Real news has
          become very difficult to parody because it keeps doing the parody
          itself. These publications do it properly — on purpose, with a label.
        </p>
        <p>
          Every entry below publishes invented stories written for entertainment.
          None of them are trying to deceive you — which is the whole difference
          between satire and fake news, and we have{" "}
          <Link href="/satire-vs-fake-news">a page about that too</Link>.
        </p>

        <h2>The reading list</h2>
        <ul>
          {sites.map((s) => (
            <li key={s.name}>
              <a href={s.url} rel="noopener noreferrer">
                <strong>{s.name}</strong>
              </a>{" "}
              — {s.note}
            </li>
          ))}
        </ul>

        <h2>What makes a site a satirical news site</h2>
        <p>
          Three things, and all three matter. The content is fictional. The
          intent is entertainment or criticism, never deception. And the site
          tells you it&apos;s joking — in a disclaimer, an about page, or in our
          case a label bolted onto{" "}
          <Link href="/articles/washington-can-t-agree-who-to-blame-for-nvidia">
            every single article
          </Link>
          . A site that invents stories and <em>doesn&apos;t</em> tell you is not
          a satire site. It is the other thing.
        </p>

        <h2>Why we built another one</h2>
        <p>
          Most satire publications are proudly regional — the Onion is American,
          the Betoota Advocate is Australian, Waterford Whispers is Irish. The
          Daily Absurd covers the whole ridiculous planet: politics, technology,
          sport, science, and whatever the baboons of Cape Town are doing this
          week. Twice a day, an editorial pipeline of software agents finds real
          events and we make them worse, lovingly.
        </p>
        <p>
          Start with our <Link href="/category">sections</Link>, or get the
          nonsense delivered via the{" "}
          <Link href="/newsletter">Absurd Dispatch</Link>.
        </p>
      </PageShell>
    </>
  );
}

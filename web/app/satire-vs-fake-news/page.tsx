import type { Metadata } from "next";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Satire vs Fake News: What's the Difference?",
  description:
    "Satire vs fake news explained: one is a labelled joke meant to entertain, the other is a lie meant to deceive. How to tell them apart, and why the label matters.",
  alternates: { canonical: `${site.url}/satire-vs-fake-news` },
};

export default function SatireVsFakeNews() {
  return (
    <PageShell
      kicker="Media Literacy, Sadly Necessary"
      title="Satire vs. Fake News: One Is a Joke, the Other Is a Lie"
    >
      <p>
        People mix these up constantly, which is understandable — they can look
        identical on a screenshot — and dangerous, because the difference is the
        entire point. Here is the short version:{" "}
        <strong>
          satire wants you to know it&apos;s false; fake news wants you to
          believe it&apos;s true.
        </strong>
      </p>

      <h2>What satire is</h2>
      <p>
        Satire is fiction wearing a news costume. It takes real events,
        institutions and public figures and exaggerates, distorts or inverts
        them to make a point — usually a critical one. The Onion, Reductress
        and, on our better days, The Daily Absurd are examples. A satirical
        article is labelled as satire, links back to the real event it is
        mocking, and hopes you share it because it&apos;s funny — not because
        you were fooled.
      </p>

      <h2>What fake news is</h2>
      <p>
        Fake news is fabricated content dressed as journalism and published to
        deceive: invented quotes presented as real, doctored images presented as
        evidence, made-up statistics presented as fact. The goal is usually
        money (rage clicks), influence (propaganda), or both. It does not label
        itself. Labelling itself would defeat the purpose, because the purpose
        is you believing it.
      </p>

      <h2>The actual differences</h2>
      <ul>
        <li>
          <strong>Intent.</strong> Satire exists to entertain and to criticise.
          Fake news exists to make you believe something false — about a person,
          an election, a war, a cure.
        </li>
        <li>
          <strong>Disclosure.</strong> Satire sites tell you what they are,
          loudly and repeatedly. We put a SATIRE badge on every article and a
          disclosure in our page metadata. Fake news hides its nature; the
          disguise is the product.
        </li>
        <li>
          <strong>Relationship to the truth.</strong> Satire points at a real
          event and says &quot;look how absurd this already is.&quot; Fake news
          points at an invented event and insists it happened.
        </li>
        <li>
          <strong>Reaction to being caught.</strong> When a satire site fools
          someone, it corrects the impression — being believed is a failure.
          When fake news is caught, it moves to a new domain.
        </li>
      </ul>

      <h2>How to tell them apart in the wild</h2>
      <ul>
        <li>
          Check the site&apos;s about page or disclaimer. Satire publications
          brag about being fake. Deceptive ones brag about being suppressed
          truth.
        </li>
        <li>
          Look for the story anywhere else. A real event gets coverage; an
          invented one exists on exactly one site and four hundred repost
          accounts.
        </li>
        <li>
          Read past the headline. Satire usually keeps winking — escalating
          absurdity, obviously fictional quotes, a joke in the last line.
        </li>
        <li>
          Ask who benefits if you believe it. If the answer is &quot;the
          site&apos;s donation page&quot; or &quot;one side of an election&quot;,
          be suspicious.
        </li>
      </ul>

      <h2>Where we fit</h2>
      <p>
        The Daily Absurd is satire, and we work hard to keep it unmistakable.
        Every article carries a persistent satire label, names the real event
        that inspired it, and bans invented quotes or allegations about real
        identifiable people. The full rules are in our{" "}
        <Link href="/editorial-policy">editorial policy</Link> and{" "}
        <Link href="/disclaimer">satire disclaimer</Link>, and if you&apos;re
        still deciding whether to trust us, don&apos;t — that is genuinely the
        correct instinct for reading anything on the internet.
      </p>
      <p>
        If you came here looking for actual fake news, we can only offer{" "}
        <Link href="/satirical-news-sites">recommendations of other satire sites</Link>{" "}
        and our sincere concern.
      </p>
    </PageShell>
  );
}

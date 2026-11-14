import PageShell from "@/components/PageShell";

export const metadata = { title: "Satire Disclaimer" };

export default function Disclaimer() {
  return (
    <PageShell kicker="Please Read Before Believing Anything" title="Satire Disclaimer">
      <p>
        <strong>
          The Daily Absurd is a satirical publication. All articles, quotes,
          statistics and events described on this website are fictional and
          created for comedic and entertainment purposes only.
        </strong>
      </p>
      <p>
        Any resemblance to actual events beyond the real news stories that
        inspired each article, or to actual persons quoted saying things they
        demonstrably did not say, is intentional — that is how satire works.
      </p>
      <p>
        Nothing on this site constitutes news, factual reporting, advice, or an
        official statement of any kind. If you are looking for reliable
        information about current events, please consult a real news
        organisation. There are several excellent ones, and at least three of
        them are occasionally right.
      </p>
    </PageShell>
  );
}

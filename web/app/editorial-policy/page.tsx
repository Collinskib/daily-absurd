import PageShell from "@/components/PageShell";

export const metadata = { title: "Editorial Policy" };

export default function EditorialPolicy() {
  return (
    <PageShell kicker="Standards, Loosely Enforced" title="Editorial Policy">
      <h2>Satire first</h2>
      <p>
        Every article on The Daily Absurd is a fictional, satirical work inspired
        by real events. We do not publish factual reporting. Nothing on this site
        should be relied upon as a source of news, information, or truth of any
        kind.
      </p>
      <h2>Our rules</h2>
      <ul>
        <li>
          <strong>Real events, fictional treatment.</strong> Each story names the
          real event that inspired it. The story itself — its details, quotes and
          outcomes — is invented.
        </li>
        <li>
          <strong>No fake quotes from real people.</strong> We never put invented
          words in the mouths of identifiable real individuals.
        </li>
        <li>
          <strong>No invented allegations.</strong> We do not fabricate crimes,
          corruption, misconduct, medical conditions or other damaging claims
          about identifiable real people.
        </li>
        <li>
          <strong>Clearly labelled.</strong> Article pages carry a persistent
          SATIRE label, and our metadata declares the fictional nature of the
          content.
        </li>
        <li>
          <strong>No fake emergencies.</strong> We never publish content that
          could be mistaken for an emergency alert, public safety announcement,
          or genuine official statement.
        </li>
        <li>
          <strong>Punch up, not down.</strong> The targets of our humour are
          institutions, absurdity, power and the universal silliness of modern
          life — not vulnerable people.
        </li>
      </ul>
      <h2>Corrections</h2>
      <p>
        If a joke lands on a factual error in the real-world context we cite, we
        will correct the context. We will not, however, correct the jokes. They
        were never true to begin with; that is rather the point.
      </p>
    </PageShell>
  );
}

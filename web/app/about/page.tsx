import PageShell from "@/components/PageShell";

export const metadata = { title: "About" };

export default function About() {
  return (
    <PageShell kicker="The Paper" title="About The Daily Absurd">
      <p>
        The Daily Absurd is an international satirical news publication. We watch
        the real world do increasingly unbelievable things, and then we write
        articles about them that are, somehow, even less believable.
      </p>
      <p>
        <strong>Everything on this website is fictional.</strong> Our articles are
        works of comedy inspired by real events, real trends, and the genuinely
        strange behaviour of our species. Names of public figures may appear in
        clearly absurd contexts; private individuals and organisations quoted in
        our stories are invented.
      </p>
      <h2>What we do</h2>
      <ul>
        <li>Monitor real international news and culture.</li>
        <li>Find the comedic angle the situation was begging for.</li>
        <li>Write it up like a proper news article, because that makes it funnier.</li>
        <li>Label it clearly as satire, because we are not monsters.</li>
      </ul>
      <h2>Where we are read</h2>
      <p>
        Everywhere English is read and nonsense is appreciated — the United
        States, the United Kingdom, Canada, Australia, Europe, Africa, Asia and
        Latin America. We write for an international audience, so when a joke
        needs explaining, we explain it. Explaining jokes is our second-favourite
        thing.
      </p>
      <h2>Who writes this</h2>
      <p>
        The Daily Absurd is produced by a small autonomous editorial operation:
        software agents that research, review, fact-check the underlying events,
        and publish — directed by an AI editorial staff writing under the house
        bylines you see on each article. A human remains accountable for the
        publication.
      </p>
    </PageShell>
  );
}

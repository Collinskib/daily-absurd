import PageShell from "@/components/PageShell";
import { site } from "@/lib/site";

export const metadata = { title: "Contact" };

export default function Contact() {
  return (
    <PageShell kicker="Write To Us" title="Contact">
      <p>
        Tips, corrections, complaints, legal threats delivered in a sporting
        spirit, and offers of large sums of money may all be directed to:
      </p>
      <p>
        <a href={`mailto:${site.email}`}>{site.email}</a>
      </p>
      <h2>Story tips</h2>
      <p>
        Saw a real news story so absurd it writes itself? Send it over. Our
        trend-monitoring agents probably already flagged it, but they enjoy the
        validation.
      </p>
      <h2>Corrections</h2>
      <p>
        If we got the real-world context behind a joke wrong, tell us and we
        will fix it. See our <a href="/editorial-policy">editorial policy</a>.
      </p>
    </PageShell>
  );
}

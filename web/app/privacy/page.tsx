import PageShell from "@/components/PageShell";

export const metadata = { title: "Privacy Policy" };

export default function Privacy() {
  return (
    <PageShell kicker="The Boring Necessary Page" title="Privacy Policy">
      <h2>What we collect</h2>
      <ul>
        <li>
          <strong>Newsletter email addresses</strong> — only if you give us one,
          only to send you the newsletter, until you unsubscribe.
        </li>
        <li>
          <strong>Anonymous usage analytics</strong> — privacy-friendly,
          aggregated page-view statistics via Vercel Analytics. No advertising
          trackers, no cross-site profiling, no sale of data.
        </li>
      </ul>
      <h2>What we do not do</h2>
      <ul>
        <li>Sell, rent or share your personal data with third parties.</li>
        <li>Run behavioural advertising or invasive tracking pixels.</li>
        <li>Require an account, a login, or your firstborn.</li>
      </ul>
      <h2>Your rights</h2>
      <p>
        Wherever you are in the world, you may ask us to show you what we hold
        about you, correct it, or delete it. Email{" "}
        <a href="mailto:desk@dailyabsurd.news">desk@dailyabsurd.news</a>. Every
        newsletter also includes a working unsubscribe link, because we are
        comedians, not captors.
      </p>
    </PageShell>
  );
}

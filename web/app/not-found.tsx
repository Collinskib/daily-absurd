import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-24 text-center">
      <p className="font-serif font-black text-[8rem] leading-none text-vermilion">404</p>
      <h1 className="font-serif font-bold text-3xl mt-4">
        This page is missing. Unlike our stories, this one wasn&apos;t intentional.
      </h1>
      <p className="mt-4 font-serif italic text-lg text-ink-soft">
        It may never have existed — which, to be fair, is true of everything we publish.
      </p>
      <Link href="/" className="mt-8 inline-block border-2 border-ink bg-ink text-paper px-6 py-3 kicker hover:bg-vermilion hover:border-vermilion transition-colors">
        Back to the front page
      </Link>
    </div>
  );
}

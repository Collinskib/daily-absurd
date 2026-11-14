export default function PageShell({
  kicker,
  title,
  children,
}: {
  kicker: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-10">
      <p className="kicker text-vermilion">{kicker}</p>
      <h1 className="font-serif font-black text-4xl sm:text-5xl mt-2 border-b-4 border-ink pb-6 mb-8">
        {title}
      </h1>
      <div className="article-body [&_h2]:font-serif [&_h2]:font-bold [&_h2]:text-2xl [&_h2]:mt-10 [&_h2]:mb-4 [&_h2]:text-ink [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:mb-6 [&_li]:mb-2 [&_a]:text-vermilion [&_a]:underline">
        {children}
      </div>
    </div>
  );
}

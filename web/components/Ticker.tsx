export default function Ticker({ items }: { items: string[] }) {
  if (items.length === 0) {
    items = ["The world remains serious. We remain otherwise."];
  }
  const seq = [...items, ...items];
  return (
    <div className="bg-ink text-paper overflow-hidden py-1.5" aria-hidden="true">
      <div className="ticker-track">
        {seq.map((h, i) => (
          <span key={i} className="mx-6 text-[0.72rem] font-bold uppercase tracking-[0.14em]">
            {h} <span className="text-vermilion ml-6">◆</span>
          </span>
        ))}
      </div>
    </div>
  );
}

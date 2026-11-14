import { ImageResponse } from "next/og";
import { getArticle, categoryName } from "@/lib/articles";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OgImage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const a = getArticle(slug);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#faf6ec",
          padding: 64,
          border: "16px solid #16130e",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 30, fontWeight: 900, letterSpacing: 6, color: "#e63b12" }}>
            SATIRE
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "#6f675a", letterSpacing: 3 }}>
            {a ? categoryName(a.category).toUpperCase() : ""}
          </div>
        </div>
        <div
          style={{
            fontSize: a && a.headline.length > 80 ? 56 : 68,
            fontWeight: 800,
            lineHeight: 1.05,
            color: "#16130e",
            fontFamily: "Georgia, serif",
          }}
        >
          {a?.headline ?? "The Daily Absurd"}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            borderTop: "4px solid #16130e",
            paddingTop: 24,
          }}
        >
          <div style={{ display: "flex", fontSize: 40, fontWeight: 900, fontFamily: "Georgia, serif", color: "#16130e" }}>
            The Daily&nbsp;<span style={{ color: "#e63b12", fontStyle: "italic" }}>Absurd</span>
          </div>
          <div style={{ fontSize: 22, color: "#6f675a" }}>100% fictional. 0% boring.</div>
        </div>
      </div>
    ),
    size,
  );
}

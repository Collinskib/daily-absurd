export const site = {
  name: "The Daily Absurd",
  tagline: "The World Is Serious. We Don't Have To Be.",
  description:
    "The Daily Absurd is an international satirical news publication — daily parody articles and invented headlines inspired by real events, written for entertainment, not information.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3100",
  email: "desk@dailyabsurd.news",
  social: {
    x: "https://x.com/dailyabsurd",
    facebook: "https://facebook.com/dailyabsurd",
    instagram: "https://instagram.com/dailyabsurd",
    youtube: "https://youtube.com/@dailyabsurd",
    pinterest: "https://pinterest.com/dailyabsurd",
  },
} as const;

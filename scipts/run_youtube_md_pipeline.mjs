/**
 * Runs the same pipeline as fetch_youtube_transcripts_md.py (for environments without working python3).
 *
 *   export SUPADATA_API_KEY="..."
 *   node run_youtube_md_pipeline.mjs
 */

import { mkdirSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = join(__dirname, "youtube-transcripts");

const SUPADATA_TRANSCRIPT_URL = "https://api.supadata.ai/v1/youtube/transcript";
const YOUTUBE_OEMBED = "https://www.youtube.com/oembed";

const EXPERT_FALLBACK = {
  Ikndrts8NQU: "Alex Berman",
  "4ISPFDktcR0": "Kennedy",
};

const VIDEOS = [
  {
    videoId: "PXl4tub30d0",
    url: "https://www.youtube.com/watch?v=PXl4tub30d0",
    expert: "Dan Martell",
  },
  {
    videoId: "WsMmo2VfcW4",
    url: "https://www.youtube.com/watch?v=WsMmo2VfcW4",
    expert: "Alex Berman",
  },
  {
    videoId: "Ikndrts8NQU",
    url: "https://www.youtube.com/watch?v=Ikndrts8NQU",
    expert: null,
  },
  {
    videoId: "_ryHpIU9qVY",
    url: "https://www.youtube.com/watch?v=_ryHpIU9qVY",
    expert: "Kennedy",
  },
  {
    videoId: "4ISPFDktcR0",
    url: "https://www.youtube.com/watch?v=4ISPFDktcR0",
    expert: null,
  },
  {
    videoId: "y813lOz4M5U",
    url: "https://www.youtube.com/watch?v=y813lOz4M5U",
    expert: "Charlie Morgan",
  },
  {
    videoId: "q7-8vKHyq0c",
    url: "https://www.youtube.com/watch?v=q7-8vKHyq0c",
    expert: "Val Geisler",
  },
  {
    videoId: "5gPWZ5-w_yw",
    url: "https://www.youtube.com/watch?v=5gPWZ5-w_yw",
    expert: "Joanna Wiebe",
  },
  {
    videoId: "ACMED_IDZb8",
    url: "https://www.youtube.com/watch?v=ACMED_IDZb8",
    expert: "Adam Robinson",
  },
  {
    videoId: "OeKqrzUvkJM",
    url: "https://www.youtube.com/watch?v=OeKqrzUvkJM",
    expert: "Chase Dimond",
  },
];

const IMPROVED = {
  PXl4tub30d0: `- **Lifecycle map:** Design email around New Lead -> Prospect nurture -> Active customer -> Long-term nurture, not disconnected campaigns.
- **Progressive asks:** Move people A->B->C; avoid jumping to the big close in one touch.
- **Operating rules:** Echo real customer language, treat email as a compounding asset, and give every send one obvious next step.`,
  WsMmo2VfcW4: `- **Signal-first hooks:** Use AI to surface non-obvious personal and affiliation cues, not just merge fields.
- **Tribal alignment:** Reflect shared beliefs, communities, and identity to earn trust in cold outreach.
- **Personalization depth:** Aim for relevance at the identity level; weigh creative boldness against brand and compliance risk.`,
  Ikndrts8NQU: `- **Targeting beats brute force:** More sends will not fix weak ICP, list hygiene, or offer-market fit.
- **Prove on a slice:** Pilot on a tight, high-fit cohort (~200); scale only when replies prove the motion works.
- **Infrastructure is downstream:** Domains, inboxes, and warm-up amplify a working motion; they do not substitute for it.`,
  _ryHpIU9qVY: `- **Dual engines:** Pair automated onboarding with a disciplined daily content rhythm.
- **Story bank:** Capture personal stories and translate each into a revenue message (AI can structure; voice stays human).
- **Conversion hygiene:** Every email builds connection, carries one CTA, and hands off to a focused landing experience (Faster / Easier / More certain).`,
  "4ISPFDktcR0": `- **Stack the offer ladder:** Flagship core + recurring driver + timely upsell + premium tier to deepen ARPU.
- **Monetize the journey:** Multiple on-ramps feed one coherent path; email moves people between stages instead of closing entirely in the inbox.
- **LTV over vanity sends:** Optimize depth per customer and monetization layers instead of chasing raw message volume.`,
  y813lOz4M5U: `- **Offer clarity wins:** Cold email scales when the market and promise are sharp; clever copy cannot rescue a fuzzy offer.
- **Avatar depth > one-off research:** Understand fears, desires, and beliefs at segment level so one message can scale.
- **High-reply skeleton:** Curiosity-led subject + aligned preview + short body that leads with the offer and a single CTA; avoid heavy footers and me-first storytelling.`,
  "q7-8vKHyq0c": `- **Retention economics:** Most upside sits in existing customers; design email as an LTV engine, not only net-new acquisition.
- **Segment deliberately:** Separate ghosts (engaged non-buyers) from zombies (one-time buyers) and tailor win-backs.
- **Contextual triggers:** Re-engagement needs a behavioral or timing reason, not generic checking in.
- **Customer-centric proof:** Prefer you asked, we built narratives over brand-centric announcements; mine win-backs and feedback for signal.`,
  "5gPWZ5-w_yw": `- **SaaS is a stakeholder game:** The buyer is often not the end user; write so PMs and marketers can approve and ship.
- **Constraints are the brief:** Short, on-brand, template-friendly beats clever that never clears legal or brand.
- **Repeatable lifecycle scaffold:** Headline -> hook -> payoff -> feature proof (visual + rule-of-three explanation) -> CTA.
- **Ship, test, then bend rules:** Win inside organizational constraints before pushing novel formats or tone.`,
  ACMED_IDZb8: `- **Deliverability is the product:** Infrastructure and inbox placement matter as much as copy; great messaging in spam is worthless.
- **Warm before you pitch:** Use social and brand touchpoints so cold email behaves more like follow-up than a blind intrusion.
- **Orchestrate channels:** Pair demand creation (e.g. LinkedIn) with email for conversion; add timing triggers (e.g. site visits) for intent spikes.
- **Systems over one-off campaigns:** Layer waitlists, outbound, and retargeting; test long enough for signal before rewriting strategy.`,
  OeKqrzUvkJM: `- **Acquisition system, not one tactic:** Fast list growth came from coordinated channels, not a single email hack.
- **Cold email at scale:** Behavior-informed personalization and strong data quality powered top-of-funnel capture.
- **Loops beat bursts:** Referral giveaways and partnerships created repeatable compounding growth.
- **Buy or rent distribution:** Acquiring or repurposing existing audiences accelerated reach versus starting from zero.
- **Pre-launch leverage:** Early-access windows captured emails before expectations hardened; ongoing value retained subscribers.`,
};

function normalizeExpert(raw, videoId) {
  if (raw) {
    const n = raw.replace(/\n/g, " ").trim();
    if (n.toLowerCase().startsWith("charlie morgan")) return "Charlie Morgan";
    if (n.toLowerCase().includes("kennedy")) return "Kennedy";
    return n;
  }
  return EXPERT_FALLBACK[videoId] ?? "Unknown";
}

function slugify(title) {
  return (
    title
      .toLowerCase()
      .trim()
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || "video"
  );
}

const FILLER = /\b(?:um|uh|ah+|eh|er|erm|you know|like)\b[,.]*/gi;
const BRACKET_TS = /\[[\d:]+\]/g;
const PAREN_TS = /\(\s*\d+:\d+(?::\d+)?\s*\)/g;

function cleanTranscript(raw) {
  let t = raw.trim();
  t = t.replace(BRACKET_TS, " ");
  t = t.replace(PAREN_TS, " ");
  t = t.replace(/\([^)]*(?:music|Music|applause|laughter)[^)]*\)/g, " ");
  t = t.replace(/\[[^\]]*(?:Music|music|applause|laughter)[^\]]*\]/g, " ");
  t = t.replace(FILLER, " ");
  t = t.replace(/[ \t]+/g, " ");
  t = t.replace(/\s+([.,!?])/g, "$1");
  const parts = t.split(/(?<=[.!?])\s+/);
  const paras = [];
  let buf = [];
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i].trim();
    if (!p) continue;
    buf.push(p);
    if (buf.length >= 4 || i === parts.length - 1) {
      paras.push(buf.join(" "));
      buf = [];
    }
  }
  if (buf.length) paras.push(buf.join(" "));
  let out = paras.join("\n\n");
  out = out.replace(/^-\s+/m, "");
  return out;
}

async function oembed(url) {
  const u = new URL(YOUTUBE_OEMBED);
  u.searchParams.set("url", url);
  u.searchParams.set("format", "json");
  const r = await fetch(u);
  if (!r.ok) throw new Error(`oEmbed ${r.status}`);
  return r.json();
}

async function fetchTranscript(apiKey, url) {
  const u = new URL(SUPADATA_TRANSCRIPT_URL);
  u.searchParams.set("url", url);
  u.searchParams.set("text", "true");
  const r = await fetch(u, { headers: { "x-api-key": apiKey } });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`Supadata ${r.status}: ${txt}`);
  }
  const data = await r.json();
  const content = data.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content.map((c) => (c && c.text) || "").join("\n");
  }
  throw new Error(`Bad transcript shape: ${JSON.stringify(data).slice(0, 200)}`);
}

function buildMd({ title, expert, channel, url, highlights, transcript }) {
  const secHigh = `${String.fromCodePoint(0x1f3af)} Key Highlights`;
  const secTrans = `${String.fromCodePoint(0x1f4dd)} Full Transcript`;
  return (
    `# ${title}\n` +
    `**Expert:** ${expert} | **Channel:** ${channel}\n` +
    `**Source Link:** ${url}\n` +
    `\n---\n\n## ${secHigh}\n` +
    `${highlights}\n\n---\n\n## ${secTrans}\n` +
    `${transcript}\n`
  );
}


const apiKey = process.env.SUPADATA_API_KEY?.trim();
if (!apiKey) {
  console.error("Set SUPADATA_API_KEY");
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });

const written = [];
for (const v of VIDEOS) {
  const expert = normalizeExpert(v.expert, v.videoId);
  const meta = await oembed(v.url);
  const title = meta.title;
  const channel = meta.author_name;
  const slug = slugify(title);
  const raw = await fetchTranscript(apiKey, v.url);
  const transcript = cleanTranscript(raw);
  const highlights = IMPROVED[v.videoId] ?? "- (No highlights.)";
  const md = buildMd({ title, expert, channel, url: v.url, highlights, transcript });
  const outPath = join(OUTPUT_DIR, `${slug}.md`);
  writeFileSync(outPath, md, "utf8");
  written.push(outPath);
  console.log("Wrote", outPath);
}

console.log(JSON.stringify({ count: written.length, files: written }, null, 2));

const fs = require("fs");
const path = require("path");

const base = path.join(process.cwd(), "research", "youtube-transcripts");
const files = [
  "tk-kader-email-strategy.txt",
  "alex-berman-cold-email-tactics.txt",
];

const removeTimestamps = (text) =>
  text
    .replace(/\[\d{1,2}:\d{2}(?::\d{2})?\]/g, " ")
    .replace(/\b\d{1,2}:\d{2}(?::\d{2})?\b/g, " ");

const normalize = (text) => text.replace(/\n/g, " ").replace(/\s+/g, " ").trim();

const splitSentences = (text) =>
  text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => (/[.!?]$/.test(s) ? s : `${s}.`))
    .map((s) => (/^[a-z]/.test(s) ? `${s[0].toUpperCase()}${s.slice(1)}` : s));

const dedupe = (sentences) => {
  const seen = new Set();
  const out = [];
  for (const sentence of sentences) {
    const key = sentence
      .toLowerCase()
      .replace(/[^a-z0-9 ]+/g, "")
      .replace(/\s+/g, " ")
      .trim();
    if (!key || key.length < 3 || seen.has(key)) continue;
    seen.add(key);
    out.push(sentence);
  }
  return out;
};

const buildParagraphs = (sentences, linesPerParagraph = 4) => {
  const chunks = [];
  for (let i = 0; i < sentences.length; i += linesPerParagraph) {
    chunks.push(sentences.slice(i, i + linesPerParagraph).join(" "));
  }
  return chunks.join("\n\n").trim();
};

const generateInsights = (sentences) => {
  const joined = sentences.join(" ").toLowerCase();
  const patterns = [
    [
      /\bsequence|nurture|onboard|indoctrination\b/,
      "Build a deliberate email sequence for each buyer stage, from new lead to long-term nurture.",
    ],
    [
      /\bcta|call to action|move|step [a-z]\b/,
      "Give every email one clear next step so readers progress gradually instead of being pushed to a final offer too early.",
    ],
    [
      /\basset|list|email list|collect\b/,
      "Treat your email list as a core business asset and review list-growth metrics every week.",
    ],
    [
      /\bvoice|tone|friendly|template|approved\b/,
      "Match the expected brand voice and layout conventions first to increase internal approval speed.",
    ],
    [
      /\becho|sales call|transcrib|language|copy\b/,
      "Use customer language from calls and interviews in your copy to increase relevance and response.",
    ],
    [
      /\bfeature|gif|image|button\b/,
      "Structure product emails with a strong hook, brief feature context, visual proof, and a focused CTA button.",
    ],
    [
      /\btest|a\/b|control|data\b/,
      "Run A/B tests against control emails and improve by iteration rather than rewriting everything at once.",
    ],
    [
      /\bcustomer|support|engage|expansion|upsell\b/,
      "Create post-purchase emails that drive activation, support clarity, and expansion revenue.",
    ],
  ];

  const selected = [];
  for (const [regex, message] of patterns) {
    if (regex.test(joined)) selected.push(message);
    if (selected.length >= 7) break;
  }

  const fallback = [
    "Write concise emails that are easy to scan and avoid unnecessary complexity.",
    "Lead with audience pain points before presenting product features.",
    "Keep messaging consistent across campaigns to build trust over time.",
    "Prioritize practical value in every email so unsubscribing feels like a loss.",
    "Regularly refresh campaigns using proven high-performing angles.",
    "Segment audiences by behavior so each message stays contextually relevant.",
    "Document your campaign logic so new team members can execute consistently.",
  ];

  for (const item of fallback) {
    if (selected.length >= 5) break;
    if (!selected.includes(item)) selected.push(item);
  }

  return selected.slice(0, 7);
};

for (const file of files) {
  const inputPath = path.join(base, file);
  const outputPath = path.join(base, file.replace(/\.txt$/, "_cleaned.txt"));
  const raw = fs.readFileSync(inputPath, "utf8");
  const normalized = normalize(removeTimestamps(raw));
  const sentences = dedupe(splitSentences(normalized));
  const transcript = buildParagraphs(sentences, 4);
  const insights = generateInsights(sentences);

  const header = `# Video Title: ${path.parse(file).name}\n# Source: YouTube\n# Cleaned Transcript\n\n`;
  const insightsBlock =
    "## Key Insights (AI-generated summary)\n" + insights.map((x) => `- ${x}`).join("\n");
  const finalText = `${header}${transcript}\n\n${insightsBlock}\n`;

  fs.writeFileSync(outputPath, finalText, { encoding: "utf8" });
  console.log(`Success: processed ${file} -> ${path.basename(outputPath)}`);
}

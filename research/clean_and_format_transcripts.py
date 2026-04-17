import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent / "youtube-transcripts"
TARGET_FILES = [
    "tk-kader-email-strategy.txt",
    "alex-berman-cold-email-tactics.txt",
]


def remove_timestamps(text: str) -> str:
    patterns = [
        r"\[\d{1,2}:\d{2}(?::\d{2})?\]",
        r"\b\d{1,2}:\d{2}(?::\d{2})?\b",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned)
    return cleaned


def normalize_spacing(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    rough = re.split(r"(?<=[.!?])\s+", text)
    sentences = []
    for item in rough:
        s = item.strip()
        if not s:
            continue

        # Try to fix sentence fragments missing terminal punctuation.
        if not re.search(r"[.!?]$", s):
            s += "."

        # Capitalize likely sentence starts.
        if s and s[0].islower():
            s = s[0].upper() + s[1:]

        sentences.append(s)
    return sentences


def dedupe_sentences(sentences: list[str]) -> list[str]:
    seen = set()
    unique = []
    for s in sentences:
        key = re.sub(r"[^a-z0-9 ]+", "", s.lower()).strip()
        key = re.sub(r"\s+", " ", key)
        if not key or len(key) < 3:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)
    return unique


def build_paragraphs(sentences: list[str], lines_per_para: int = 4) -> str:
    chunks = []
    for i in range(0, len(sentences), lines_per_para):
        chunk = sentences[i : i + lines_per_para]
        chunks.append(" ".join(chunk))
    return "\n\n".join(chunks).strip()


def generate_insights(sentences: list[str], min_items: int = 5, max_items: int = 7) -> list[str]:
    keyword_patterns = [
        (r"\bsequence|nurture|onboard|indoctrination\b", "Build a deliberate email sequence for each buyer stage, from new lead to long-term nurture."),
        (r"\bcta|call to action|move|step [a-z]\b", "Give every email one clear next step so readers progress gradually instead of being pushed to a final offer too early."),
        (r"\basset|list|email list|collect\b", "Treat your email list as a core business asset and review list-growth metrics every week."),
        (r"\bvoice|tone|friendly|template|approved\b", "Match the expected brand voice and layout conventions first to increase internal approval speed."),
        (r"\becho|sales call|transcrib|language|copy\b", "Use customer language from calls and interviews in your copy to increase relevance and response."),
        (r"\bfeature|gif|image|button\b", "Structure product emails with a strong hook, brief feature context, visual proof, and a focused CTA button."),
        (r"\btest|a\/b|control|data\b", "Run A/B tests against control emails and improve by iteration rather than rewriting everything at once."),
        (r"\bcustomer|support|engage|expansion|upsell\b", "Create post-purchase emails that drive activation, support clarity, and expansion revenue."),
    ]

    joined = " ".join(sentences).lower()
    insights = []
    for pattern, suggestion in keyword_patterns:
        if re.search(pattern, joined):
            insights.append(suggestion)
        if len(insights) >= max_items:
            break

    if len(insights) < min_items:
        fallback = [
            "Write concise emails that are easy to scan and avoid unnecessary complexity.",
            "Lead with audience pain points before presenting product features.",
            "Keep messaging consistent across campaigns to build trust over time.",
            "Prioritize practical value in every email so unsubscribing feels like a loss.",
            "Regularly refresh campaigns using proven high-performing angles.",
            "Segment audiences by behavior so each message stays contextually relevant.",
            "Document your campaign logic so new team members can execute consistently.",
        ]
        for item in fallback:
            if item not in insights:
                insights.append(item)
            if len(insights) >= min_items:
                break

    return insights[:max_items]


def process_file(filename: str) -> None:
    input_path = BASE_DIR / filename
    output_path = BASE_DIR / f"{input_path.stem}_cleaned.txt"

    raw = input_path.read_text(encoding="utf-8")
    text = remove_timestamps(raw)
    text = normalize_spacing(text)
    sentences = split_sentences(text)
    sentences = dedupe_sentences(sentences)

    paragraphs = build_paragraphs(sentences, lines_per_para=4)
    insights = generate_insights(sentences, min_items=5, max_items=7)

    title = input_path.stem
    header = (
        f"# Video Title: {title}\n"
        "# Source: YouTube\n"
        "# Cleaned Transcript\n\n"
    )

    insights_block = "## Key Insights (AI-generated summary)\n" + "\n".join(
        f"- {item}" for item in insights
    )

    final_text = f"{header}{paragraphs}\n\n{insights_block}\n"
    output_path.write_text(final_text, encoding="utf-8")

    print(f"Success: processed '{filename}' -> '{output_path.name}'")


def main() -> None:
    for file_name in TARGET_FILES:
        process_file(file_name)


if __name__ == "__main__":
    main()

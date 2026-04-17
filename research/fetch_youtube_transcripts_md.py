"""
Fetch YouTube transcripts via Supadata, clean them, merge CSV highlights, and write Markdown files.

Requirements:
  pip install requests

Usage:
  export SUPADATA_API_KEY="your_key"
  python3 fetch_youtube_transcripts_md.py

CSV path: ../Keywords (4).csv (repo root)
Output: ./youtube-transcripts/<slugified-title>.md
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "Keywords (4).csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "youtube-transcripts"

SUPADATA_TRANSCRIPT_URL = "https://api.supadata.ai/v1/youtube/transcript"
YOUTUBE_OEMBED = "https://www.youtube.com/oembed"

EXPERT_BY_VIDEO_ID: dict[str, str] = {
    "Ikndrts8NQU": "Alex Berman",
    "4ISPFDktcR0": "Kennedy",
}

# Row 10 in the sheet links a case-study page; we use a long-form YouTube interview for the transcript.
CHASE_DIMOND = {
    "video_id": "OeKqrzUvkJM",
    "url": "https://www.youtube.com/watch?v=OeKqrzUvkJM",
    "expert": "Chase Dimond",
    "highlight": (
        "Case study notes: multi-channel acquisition to 500k subscribers; "
        "data-driven cold email; referral and giveaway loops; leveraged audiences; "
        "ambassadors; pre-launch email capture."
    ),
}

FILLER_RE = re.compile(
    r"\b(?:um|uh|ah+|eh|er|erm|you know|like)\b[,.]*",
    re.IGNORECASE,
)
BRACKET_TS_RE = re.compile(r"\[[\d:]+\]")
PAREN_TS_RE = re.compile(r"\(\s*\d+:\d+(?::\d+)?\s*\)")
MULTISPACE_RE = re.compile(r"[ \t]+")


def get_api_key() -> str:
    key = os.environ.get("SUPADATA_API_KEY", "").strip()
    if not key:
        print("Set SUPADATA_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)
    return key


def slugify_title(title: str) -> str:
    s = title.lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "video"


def normalize_expert(raw: str | None, video_id: str) -> str:
    if raw:
        name = raw.replace("\n", " ").strip()
        if name.lower().startswith("charlie morgan"):
            return "Charlie Morgan"
        if "kennedy" in name.lower():
            return "Kennedy"
        return name
    return EXPERT_BY_VIDEO_ID.get(video_id, "Unknown")


def load_csv_videos() -> list[dict[str, Any]]:
    rows: list[list[str]] = []
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        blob = " ".join(x for x in row if x)
        m = re.search(r"(https://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+))", blob)
        if not m:
            continue
        url, vid = m.group(1), m.group(2)
        base_url = url.split("&")[0]
        expert = row[3].strip() if len(row) > 3 and row[3] else None
        highlight = row[-1].strip() if row[-1] else ""
        out.append(
            {
                "video_id": vid,
                "url": base_url,
                "expert": expert,
                "highlight": highlight,
            }
        )
    return out


def youtube_oembed(video_url: str) -> dict[str, Any]:
    r = requests.get(
        YOUTUBE_OEMBED,
        params={"url": video_url, "format": "json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def fetch_transcript(api_key: str, video_url: str) -> str:
    r = requests.get(
        SUPADATA_TRANSCRIPT_URL,
        headers={"x-api-key": api_key},
        params={"url": video_url, "text": "true"},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    content = data.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for chunk in content:
            if isinstance(chunk, dict) and "text" in chunk:
                parts.append(str(chunk["text"]))
        return "\n".join(parts)
    raise ValueError(f"Unexpected transcript payload: {data!r}")


def clean_transcript(raw: str) -> str:
    t = raw.strip()
    t = BRACKET_TS_RE.sub(" ", t)
    t = PAREN_TS_RE.sub(" ", t)
    t = re.sub(
        r"\([^)]*(?:music|Music|applause|laughter)[^)]*\)",
        " ",
        t,
    )
    t = re.sub(
        r"\[[^\]]*(?:Music|music|applause|laughter)[^\]]*\]",
        " ",
        t,
    )
    t = FILLER_RE.sub(" ", t)
    t = MULTISPACE_RE.sub(" ", t)
    t = re.sub(r"\s+([.,!?])", r"\1", t)
    parts = re.split(r"(?<=[.!?])\s+", t)
    paras: list[str] = []
    buf: list[str] = []
    for i, p in enumerate(parts):
        p = p.strip()
        if not p:
            continue
        buf.append(p)
        if len(buf) >= 4 or i == len(parts) - 1:
            paras.append(" ".join(buf))
            buf = []
    if buf:
        paras.append(" ".join(buf))
    text = "\n\n".join(paras)
    return re.sub(r"^-\s+", "", text, count=1, flags=re.MULTILINE)


def improve_highlights(video_id: str, expert: str, raw: str) -> str:
    _ = (expert, raw)
    improved: dict[str, str] = {
        "PXl4tub30d0": """- **Lifecycle map:** Design email around New Lead -> Prospect nurture -> Active customer -> Long-term nurture, not disconnected campaigns.
- **Progressive asks:** Move people A->B->C; avoid jumping to the big close in one touch.
- **Operating rules:** Echo real customer language, treat email as a compounding asset, and give every send one obvious next step.""",
        "WsMmo2VfcW4": """- **Signal-first hooks:** Use AI to surface non-obvious personal and affiliation cues, not just merge fields.
- **Tribal alignment:** Reflect shared beliefs, communities, and identity to earn trust in cold outreach.
- **Personalization depth:** Aim for relevance at the identity level; weigh creative boldness against brand and compliance risk.""",
        "Ikndrts8NQU": """- **Targeting beats brute force:** More sends will not fix weak ICP, list hygiene, or offer-market fit.
- **Prove on a slice:** Pilot on a tight, high-fit cohort (~200); scale only when replies prove the motion works.
- **Infrastructure is downstream:** Domains, inboxes, and warm-up amplify a working motion; they do not substitute for it.""",
        "_ryHpIU9qVY": """- **Dual engines:** Pair automated onboarding with a disciplined daily content rhythm.
- **Story bank:** Capture personal stories and translate each into a revenue message (AI can structure; voice stays human).
- **Conversion hygiene:** Every email builds connection, carries one CTA, and hands off to a focused landing experience (Faster / Easier / More certain).""",
        "4ISPFDktcR0": """- **Stack the offer ladder:** Flagship core + recurring driver + timely upsell + premium tier to deepen ARPU.
- **Monetize the journey:** Multiple on-ramps feed one coherent path; email moves people between stages instead of closing entirely in the inbox.
- **LTV over vanity sends:** Optimize depth per customer and monetization layers instead of chasing raw message volume.""",
        "y813lOz4M5U": """- **Offer clarity wins:** Cold email scales when the market and promise are sharp; clever copy cannot rescue a fuzzy offer.
- **Avatar depth > one-off research:** Understand fears, desires, and beliefs at segment level so one message can scale.
- **High-reply skeleton:** Curiosity-led subject + aligned preview + short body that leads with the offer and a single CTA; avoid heavy footers and me-first storytelling.""",
        "q7-8vKHyq0c": """- **Retention economics:** Most upside sits in existing customers; design email as an LTV engine, not only net-new acquisition.
- **Segment deliberately:** Separate ghosts (engaged non-buyers) from zombies (one-time buyers) and tailor win-backs.
- **Contextual triggers:** Re-engagement needs a behavioral or timing reason, not generic checking in.
- **Customer-centric proof:** Prefer you asked, we built narratives over brand-centric announcements; mine win-backs and feedback for signal.""",
        "5gPWZ5-w_yw": """- **SaaS is a stakeholder game:** The buyer is often not the end user; write so PMs and marketers can approve and ship.
- **Constraints are the brief:** Short, on-brand, template-friendly beats clever that never clears legal or brand.
- **Repeatable lifecycle scaffold:** Headline -> hook -> payoff -> feature proof (visual + rule-of-three explanation) -> CTA.
- **Ship, test, then bend rules:** Win inside organizational constraints before pushing novel formats or tone.""",
        "ACMED_IDZb8": """- **Deliverability is the product:** Infrastructure and inbox placement matter as much as copy; great messaging in spam is worthless.
- **Warm before you pitch:** Use social and brand touchpoints so cold email behaves more like follow-up than a blind intrusion.
- **Orchestrate channels:** Pair demand creation (e.g. LinkedIn) with email for conversion; add timing triggers (e.g. site visits) for intent spikes.
- **Systems over one-off campaigns:** Layer waitlists, outbound, and retargeting; test long enough for signal before rewriting strategy.""",
        "OeKqrzUvkJM": """- **Acquisition system, not one tactic:** Fast list growth came from coordinated channels, not a single email hack.
- **Cold email at scale:** Behavior-informed personalization and strong data quality powered top-of-funnel capture.
- **Loops beat bursts:** Referral giveaways and partnerships created repeatable compounding growth.
- **Buy or rent distribution:** Acquiring or repurposing existing audiences accelerated reach versus starting from zero.
- **Pre-launch leverage:** Early-access windows captured emails before expectations hardened; ongoing value retained subscribers.""",
    }
    body = improved.get(video_id)
    if not body:
        lines = [ln.strip("- ").strip() for ln in raw.splitlines() if ln.strip()]
        return "\n".join(f"- {ln}" for ln in lines[:12]) if lines else "- (No highlights available.)"
    return body


MD_TEMPLATE = (
    "# {title}\n"
    "**Expert:** {expert} | **Channel:** {channel}\n"
    "**Source Link:** {url}\n"
    "\n"
    "---\n"
    "\n"
    "## \U0001f3af Key Highlights\n"
    "{highlights}\n"
    "\n"
    "---\n"
    "\n"
    "## \U0001f4dd Full Transcript\n"
    "{transcript}\n"
)


def main() -> None:
    api_key = get_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = load_csv_videos()
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for v in videos:
        vid = v["video_id"]
        if vid in seen:
            continue
        seen.add(vid)
        unique.append(v)

    unique.append(
        {
            "video_id": CHASE_DIMOND["video_id"],
            "url": CHASE_DIMOND["url"],
            "expert": CHASE_DIMOND["expert"],
            "highlight": CHASE_DIMOND["highlight"],
        }
    )

    written: list[str] = []
    for v in unique:
        vid = v["video_id"]
        url = v["url"]
        expert = normalize_expert(v.get("expert"), vid)
        raw_highlight = v.get("highlight") or ""

        meta = youtube_oembed(url)
        title = meta["title"]
        channel = meta["author_name"]
        slug = slugify_title(title)
        transcript_raw = fetch_transcript(api_key, url)
        transcript = clean_transcript(transcript_raw)
        highlights = improve_highlights(vid, expert, raw_highlight)

        md = MD_TEMPLATE.format(
            title=title,
            expert=expert,
            channel=channel,
            url=url,
            highlights=highlights,
            transcript=transcript,
        )
        out_path = OUTPUT_DIR / f"{slug}.md"
        out_path.write_text(md, encoding="utf-8")
        written.append(str(out_path))
        print(f"Wrote {out_path}")

    print(json.dumps({"count": len(written), "files": written}, indent=2))


if __name__ == "__main__":
    main()

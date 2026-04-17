from pathlib import Path

import requests


API_KEY = "sd_60b1238e7031476201b0e2ef501d495c"
API_URL = "https://api.supadata.ai/v1/youtube/transcript"
OUTPUT_DIR = Path("research/youtube-transcripts")

VIDEOS = [
    (
        "https://www.youtube.com/watch?v=PXl4tub30d0",
        "tk-kader-email-strategy.txt",
    ),
    (
        "https://www.youtube.com/watch?v=5gPWZ5-w_yw",
        "alex-berman-cold-email-tactics.txt",
    ),
]


def fetch_transcript(video_url: str) -> str:
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
    }
    params = {
        "url": video_url,
        "text": "true",
    }

    response = requests.get(API_URL, headers=headers, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    content = data.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # Fallback if API returns timestamped chunks.
        return "\n".join(chunk.get("text", "") for chunk in content if isinstance(chunk, dict))

    raise ValueError(f"Unexpected transcript format for {video_url}: {data}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for video_url, filename in VIDEOS:
        transcript = fetch_transcript(video_url)
        output_path = OUTPUT_DIR / filename
        output_path.write_text(transcript, encoding="utf-8")
        print(f"Saved transcript: {output_path}")


if __name__ == "__main__":
    main()

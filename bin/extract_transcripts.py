#!/usr/bin/env python3
"""Extract raw YouTube transcripts for video IDs streamed on stdin and emit
one JSON Lines record per video to stdout, routing through a Webshare proxy
when credentials are present."""

import sys
import os
import json
import logging

# BLANK 1: bring load_dotenv into scope so we can read the local .env file
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from lib.logging_config import setup_logging

# BLANK 2: read .env from project root into the in-memory environment.
# This is a no-op in CI/production, where the platform injects env vars natively.
load_dotenv()

# Direct logging statements to a shared audit log asset
setup_logging()


def main():
    """Read video IDs from stdin, fetch each transcript (via proxy if configured),
    and write one {video_id, raw_text} JSON Lines row per video to stdout."""

    logging.info("Pipeline Step 2A (Raw Extraction) started.")

    # Ingest routing keys from the local shell environment
    proxy_user = os.getenv("WEBSHARE_USER")
    proxy_pass = os.getenv("WEBSHARE_PASSWORD")

    if proxy_user and proxy_pass:
        logging.info("Proxy credentials detected. Routing traffic to Webshare Residential network.")
        # BLANK 3: build the client with a Webshare residential proxy so YouTube
        # sees residential traffic instead of the AWS datacenter IP range.
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )
    else:
        logging.warning("No proxy credentials found. Running with direct raw local IP routing.")
        ytt_api = YouTubeTranscriptApi()

    # Process streaming IDs line-by-line from stdin
    for line in sys.stdin:
        video_id = line.strip()
        if not video_id:
            continue
        logging.info("Processing transcript extraction for video: %s", video_id)
        try:
            # Execute the modern 2026 instance lookup method
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()

            # Stitch chunks with timestamp codes preserved for the staging file
            raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])

            # BLANK 4: pack into one self-contained JSON object, emit a single
            # JSON Lines row to stdout, and flush so it streams immediately.
            payload = {"video_id": video_id, "raw_text": raw_text}
            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed to fetch YouTube transcript for %s: %s", video_id, str(e))
            continue

    logging.info("Pipeline Step 2A finished.")


if __name__ == '__main__':
    main()

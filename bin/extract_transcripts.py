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

load_dotenv()

logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


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
        ytt_api = YouTubeTranscriptApi()

    for line in sys.stdin:
        video_id = line.strip()
        if not video_id:
            continue

        try:
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()
            raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])
            payload = {"video_id": video_id, "raw_text": raw_text}
            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed to fetch transcript for %s: %s", video_id, str(e))
            continue


if __name__ == '__main__':
    main()

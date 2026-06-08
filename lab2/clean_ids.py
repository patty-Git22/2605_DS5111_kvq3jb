#!/usr/bin/env python3
"""Read YouTube video IDs from stdin and print only the valid 11-character IDs."""
import sys
import logging
import re

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_audit.log'),
        logging.StreamHandler(sys.stderr)
    ]
)


def validate_id(youtube_id):
    """Validate the YouTube video ID format."""
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return re.match(pattern, youtube_id) is not None


def main():
    """Read IDs from stdin, print valid ones, and log invalid ones."""
    try:
        for line in sys.stdin:
            youtube_id = line.strip()
            if not youtube_id:
                continue
            if validate_id(youtube_id):
                print(youtube_id)
            else:
                logging.warning('Invalid YouTube ID: %s', youtube_id)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()

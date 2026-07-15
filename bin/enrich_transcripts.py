#!/usr/bin/env python3
"""Pipeline Step 2B: enrich raw transcripts via Gemini under a strict data contract."""
import sys
import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from lib.logging_config import setup_logging
load_dotenv()

setup_logging()

# Task 2: schema contract
response_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "video_id": types.Schema(type=types.Type.STRING),
        "cleaned_text": types.Schema(type=types.Type.STRING),
        "tech_terms": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
        "book_names": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
    },
    required=["video_id", "cleaned_text", "tech_terms", "book_names"]
)

generate_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=response_schema
)

def main(argv=None):
    """Select an LLM strategy and run the enrichment stream."""
    parser = argparse.ArgumentParser(
        description="Multi-strategy transcript enrichment pipeline."
    )
    parser.add_argument(
        "--engine",
        choices=["gemini"],
        default="gemini",
        help="LLM enrichment strategy to use."
    )

    args = parser.parse_args(argv)

    logging.info("Pipeline Step 2B (LLM Enrichment) started.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
        sys.exit(1)

    strategies = {"gemini": GeminiStrategy}
    selected_strategy = strategies[args.engine](api_key)

    enricher = TranscriptEnricher(selected_strategy)
    enricher.run_stream()

    logging.info("Pipeline Step 2B (LLM Enrichment) finished.")


if __name__ == '__main__':
    sys.exit(main())


if __name__ == '__main__':
    main()

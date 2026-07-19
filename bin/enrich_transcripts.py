#!/usr/bin/env python3
"""Pipeline Step 2B: enrich raw transcripts via Gemini under a strict data contract."""
import sys
import os
import json
import logging
import argparse
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from google import genai
from google.genai import types
from lib.logging_config import setup_logging


class LLMStrategy(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class defining the enrichment strategy"""
    @abstractmethod
    def enrich(self, record: dict) -> dict:
        """Abstract base class defining the enrichment strategy"""


class GeminiStrategy(LLMStrategy):  # pylint: disable=too-few-public-methods
    """Gemini implementation of the LLM enrichment strategy."""

    def __init__(self, gemini_api_key: str):
        self.client = genai.Client(api_key=gemini_api_key)

        self.response_schema = types.Schema(
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
            required=[
                "video_id",
                "cleaned_text",
                "tech_terms",
                "book_names"
            ]
        )

        self.generate_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.response_schema
        )

    def enrich(self, record: dict) -> dict:
        video_id = record.get("video_id", "unknown")
        raw_text = record.get("raw_text", "")


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


def main():
    """Stream-enrich stdin records and emit schema-compliant JSON to stdout."""
    # TODO 1: validate key and init client inside main so imports don't trigger exit
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    logging.info("Pipeline Step 2B (LLM Enrichment) started.")

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

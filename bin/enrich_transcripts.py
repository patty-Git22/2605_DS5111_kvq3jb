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


class LLMStrategy(ABC):
    """Abstract base class defining the enrichment strategy"""
    @abstractmethod
    def enrich(self, record: dict) -> dict:
        """Abstract base class defining the enrichment strategy"""


class GeminiStrategy(LLMStrategy):
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

        prompt = (
            "You are a data engineering assistant. Given the following raw lecture "
            "transcript, return a JSON object with:\n"
            "- video_id: the original video ID (string)\n"
            "- cleaned_text: transcript with timestamps removed and cleaned up (string)\n"
            "- tech_terms: technical terms, tools, or technologies mentioned "
            "(array of strings)\n"
            "- book_names: book titles mentioned (array of strings)\n\n"
            f"video_id: {video_id}\nraw_text: {raw_text}"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=self.generate_config
            )
            return json.loads(response.text)

        except Exception as error:
            raise RuntimeError(
                f"Gemini enrichment failed for video {video_id}: {error}"
            ) from error


class TranscriptEnricher:
    """Streams transcript records through an injected LLM strategy."""
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    def run_stream(self):
        """Read JSONL from stdin and write enriched JSONL to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                logging.error("Skipping malformed line: %s", error)
                continue

            video_id = record.get("video_id", "unknown")

            try:
                enriched_record = self.strategy.enrich(record)
                sys.stdout.write(json.dumps(enriched_record) + "\n")
                sys.stdout.flush()
            except Exception as error:  # pylint: disable=broad-exception-caught
                logging.error(
                    "LLM enrichment failed for video %s: %s",
                    video_id,
                    error
                )
                continue


load_dotenv()

setup_logging()

# Task 1: validate key and init client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

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

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logging.critical("GEMINI_API_KEY is not set. Aborting pipeline.")
        return 1

    if args.engine == "gemini":
        strategy = GeminiStrategy(gemini_api_key=gemini_api_key)
    else:
        raise ValueError(f"Unknown engine: {args.engine}")

    enricher = TranscriptEnricher(strategy=strategy)
    enricher.run_stream()

    return 0


if __name__ == '__main__':
    sys.exit(main())

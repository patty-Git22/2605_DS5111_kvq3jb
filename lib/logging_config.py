#!/usr/bin/env python3
"""Shared logging configuration for pipeline stages.

Both extraction and enrichment steps write to the same audit log
using an identical format, so this setup is centralized here to
avoid duplicating the basicConfig call across scripts.
"""
import logging


def setup_logging():
    """Configure root logging to write timestamped INFO+ records to
    the shared pipeline audit log."""
    logging.basicConfig(
        filename='pipeline/logs/pipeline_audit.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

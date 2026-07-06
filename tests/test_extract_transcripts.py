"""Tests for the extract_transcripts pipeline stage, covering the happy
path, error handling, empty-input skipping, and proxy configuration."""

import sys
import io
import os
import json
import pytest

from youtube_transcript_api import YouTubeTranscriptApi

# Import the executable entry point from the pipeline package
from bin.extract_transcripts import main


class MockTranscriptContainer:
    """Mimics the .to_raw_data() array output schema without hitting the network."""
    def to_raw_data(self):
	"""Return a single mock transcript row."""
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """Happy path: one valid ID in -> exactly one JSON Lines row out, no internet."""
    # 1. Swap the live fetch for a stub returning mock data
    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # 2. Feed a fake video ID in through stdin
    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Run the loop
    main()

    # 4. Capture stdout and isolate the emitted rows
    captured_output = capsys.readouterr()
    stdout_lines = captured_output.out.strip().split("\n")

    # 5. Validate the JSON Lines contract
    assert len(stdout_lines) == 1, "Exactly one row per valid input ID."
    parsed_json_line = json.loads(stdout_lines[0])
    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_transcripts_handles_fetch_error_gracefully(monkeypatch, capsys):
    """Error path: a fetch that raises is caught, emits no row, and does not crash."""
    # 1. Stub fetch to raise, simulating an invalid / un-fetchable ID
    def exploding_fetch(self, video_id):
        raise RuntimeError("Simulated un-fetchable / invalid video ID")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", exploding_fetch)

    # 2. Feed the bad ID through stdin
    mock_input_stream = io.StringIO("bad_video_id\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Should return normally — no exception should bubble out of main()
    main()

    # 4. No JSON Lines payload should have been written for the failed ID
    captured_output = capsys.readouterr()
    assert captured_output.out.strip() == ""

def test_extract_transcripts_skips_empty_input_line(monkeypatch, capsys):
    """A blank stdin line hits `if not video_id: continue` and is skipped
    before fetch is ever called — so no output and no network access."""
    # Guard: if fetch somehow runs on a blank line, fail loudly instead of silently passing
    def fetch_should_not_run(self, video_id):
        raise AssertionError("fetch() must never be called on an empty input line")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", fetch_should_not_run)

    # Feed a single blank line into stdin
    mock_input_stream = io.StringIO("\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    # The blank line should be skipped, so nothing is emitted
    captured_output = capsys.readouterr()
    assert captured_output.out.strip() == ""


@pytest.mark.skipif(
    not (os.getenv("WEBSHARE_USER") and os.getenv("WEBSHARE_PASSWORD")),
    reason="Webshare proxy credentials (WEBSHARE_USER/WEBSHARE_PASSWORD) not configured in this environment"
)
def test_extract_transcripts_uses_proxy_when_configured(monkeypatch, capsys):
    """When Webshare proxy credentials are present in the environment, the
    pipeline should construct YouTubeTranscriptApi with a WebshareProxyConfig
    rather than a direct/unproxied client."""
    captured_kwargs = {}

    class SpyYouTubeTranscriptApi:
        """Records the kwargs it was constructed with, then behaves like
        the real client for the single fetch call in main()."""
        def __init__(self, **kwargs):
	"""Capture constructor kwargs for assertion down the road. """
            captured_kwargs.update(kwargs)

        def fetch(self, video_id):
	"""Return a mock transcript regardless of the requested video id."""
            return MockTranscriptContainer()

    monkeypatch.setattr(
        "bin.extract_transcripts.YouTubeTranscriptApi", SpyYouTubeTranscriptApi
    )

    mock_input_stream = io.StringIO("proxy_video_123\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    assert "proxy_config" in captured_kwargs, (
        "Expected YouTubeTranscriptApi to be constructed with a proxy_config "
        "when WEBSHARE_USER/WEBSHARE_PASSWORD are set."
    )

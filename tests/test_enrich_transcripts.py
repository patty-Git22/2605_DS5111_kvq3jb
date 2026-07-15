"""Tests for the enrich_transcripts pipeline stage, verifying the Gemini
enrichment loop reads stdin, calls the mocked GenAI client, and streams
schema-compliant JSON Lines output without live network requests."""
import sys
import io
import json
from bin.enrich_transcripts import main


# 1. Build a dummy container mimicking the Gemini SDK response hierarchy
class MockGeminiResponse:  # pylint: disable=too-few-public-methods
    """Mimics the .text attribute on a real Gemini SDK response object."""
    def __init__(self, text_payload):
        self.text = text_payload


def test_enrich_transcripts_streaming_pipeline(monkeypatch, capsys):
    """
    Verifies that main() reads mock lines from stdin, calls the Gemini client structure,
    and streams verified JSON objects out to stdout without making live API network requests.
    """
    # 2. Mock out the core GenAI Client methods
    def mock_generate_content(self, model, contents, config=None): # pylint: disable=unused-argument
        # Return a pre-baked, schema-compliant JSON string mimicking the model output
        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": "Welcome to class. Today we are testing mock frameworks.",
            "tech_terms": ["mock frameworks"],
            "book_names": []
        }
        return MockGeminiResponse(json.dumps(mock_data))

    # Corrected Module Target: Patch the actual Models service class inside the SDK
    from google.genai.models import Models
    monkeypatch.setattr(Models, "generate_content", mock_generate_content)

    # Satisfy the api-key guard in main() without hitting the real API
    monkeypatch.setenv("GEMINI_API_KEY", "test-dummy-key")

    # 3. Simulate your stream input pipeline using an in-memory text buffer
    mock_input_row = {
        "video_id": "ds5111_v001", "raw_text": "00:01 Welcome to class. Today we are testing mock frameworks."}
    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    # 4. Trigger the main pipeline script execution loop
    main()

    # 5. Intercept the standard console text buffers
    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    # 6. Execute data integrity validation assertions
    assert len(stdout_lines) == 1
    parsed_output = json.loads(stdout_lines[0])
    assert parsed_output["video_id"] == "ds5111_v001"
    assert "mock frameworks" in parsed_output["tech_terms"]

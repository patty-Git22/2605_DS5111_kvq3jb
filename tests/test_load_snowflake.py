"""Tests for the load_snowflake pipeline stage, verifying stdin JSON Lines are
processed into DDL and parameter-bound Snowflake inserts without live network calls."""
import sys
import io
import json
from unittest.mock import MagicMock
import pytest

from bin.load_snowflake import main


def test_load_snowflake_pipeline_ingestion_loop(monkeypatch, capsys):  # pylint: disable=unused-argument
    """Verify main() runs table DDL and safe parameter-bound insertions from stdin."""
    mock_cursor = MagicMock()
    mock_context = MagicMock()
    mock_context.cursor.return_value = mock_cursor

    import snowflake.connector  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(
        snowflake.connector, "connect", lambda **kwargs: mock_context
    )

    monkeypatch.setenv("SF_USER", "test_user")
    monkeypatch.setenv("SF_PASSWORD", "test_password")

    mock_input_stream = io.StringIO(
        '{"video_id": "test_id_001", "source": "youtube", '
        '"raw_text": "Sample content text A."}\n'
        '{"video_id": "test_id_002", "source": "podcast", '
        '"raw_text": "Sample content text B."}\n'
    )
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    try:
        main()
    except UnboundLocalError:
        pytest.fail(
            "Resource variables referenced before definition. "
            "Verify cursor initialization logic."
        )

    assert mock_cursor.execute.call_count >= 3, (
        "The database cursor should trigger table generation plus one call per row."
    )

    executed_queries = [call[0][0] for call in mock_cursor.execute.call_args_list]
    executed_bindings = [
        call[0][1] for call in mock_cursor.execute.call_args_list if len(call[0]) > 1
    ]

    assert any(
        "CREATE TABLE IF NOT EXISTS RAW_TRANSCRIPTS" in q for q in executed_queries
    ), "The script must verify target table existence before ingestion."

    insert_queries = [q for q in executed_queries if "INSERT INTO RAW_TRANSCRIPTS" in q]
    assert len(insert_queries) == 2, (
        "Exactly two SQL insert invocations should occur for two input rows."
    )

    for query in insert_queries:
        assert "PARSE_JSON(%s)" in query, (
            "The engine must pass payloads wrapped inside a PARSE_JSON call."
        )
        assert "%s" in query and "f" not in query, (
            "Security Violation: Hard-coded formatting detected. Use placeholders."
        )

    assert len(executed_bindings) == 2
    parsed_payload = json.loads(executed_bindings[0][0])
    assert parsed_payload["video_id"] == "test_id_001"

"""Pipeline Step 3: load enriched transcripts into Snowflake as VARIANT payloads."""
import sys
import os
import json
import logging
import snowflake.connector
from dotenv import load_dotenv

# Establish clean centralized diagnostic logging metrics output footprint
logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """Connect to Snowflake, ensure the target table, and stream-insert stdin rows."""
    load_dotenv()

    logging.info("Pipeline Step 3 (Snowflake Loader Node) initialized.")

    sf_user = os.getenv('SF_USER')
    sf_password = os.getenv('SF_PASSWORD')

    if not sf_user or not sf_password:
        logging.critical(
            "Missing critical Snowflake runtime credential bindings. Ingestion aborted."
        )
        sys.exit(1)

    try:
        ctx = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=os.getenv('SF_ACCOUNT'),
            warehouse=os.getenv('SF_WAREHOUSE'),
            database=os.getenv('SF_DATABASE'),
            schema=os.getenv('SF_SCHEMA'),
            role=os.getenv('SF_ROLE')
        )
        cs = ctx.cursor()
    except Exception as error:  # pylint: disable=broad-exception-caught
        logging.critical("Snowflake Authorization Context Handshake Failed: %s", error)
        sys.exit(1)

    try:
        cs.execute("""
            CREATE TABLE IF NOT EXISTS RAW_TRANSCRIPTS (
                json_payload VARIANT,
                inserted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logging.error("Failed to execute target structural validation DDL: %s", error)
        cs.close()
        ctx.close()
        sys.exit(1)

    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        try:
            json_data = json.loads(cleaned_line)

            insert_query = (
                "INSERT INTO RAW_TRANSCRIPTS (json_payload) SELECT PARSE_JSON(%s)"
            )
            cs.execute(insert_query, (json.dumps(json_data),))

            logging.info(
                "Loaded entry token item target: [%s] safely to warehouse.",
                json_data.get('video_id', 'UNKNOWN')
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            logging.error("Skipping corrupt pipeline payload stream element: %s", error)

    cs.close()
    ctx.close()
    logging.info("Pipeline Step 3 finished execution cycles cleanly.")


if __name__ == '__main__':
    main()

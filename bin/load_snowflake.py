# File location: bin/load_snowflake.py
import sys
import os
import json
import logging
import snowflake.connector
from dotenv import load_dotenv  # <-- Added to support standard .env loading

# Establish clean centralized diagnostic logging metrics output footprint
logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize the environment variables from the local .env file
    load_dotenv()  # <-- Added to ensure os.getenv() does not return None

    logging.info("Pipeline Step 3 (Snowflake Loader Node) initialized.")

    # -------------------------------------------------------------------------
    # TODO 1: Environment Handshake & Connection Isolation Engine [RESOLVED]
    # Securely retrieve database context variables from the shell environment.
    # If key credentials (USER/PASSWORD) are missing, log a critical alert and crash out.
    # Open your connection context engine using the native connector framework.
    # -------------------------------------------------------------------------
    sf_user = os.getenv('SF_USER')
    sf_password = os.getenv('SF_PASSWORD')
    
    if not sf_user or not sf_password:
        logging.critical("Missing critical Snowflake runtime credential bindings. Ingestion aborted.")
        sys.exit(1)
        
    try:
        # Pass the pre-extracted user/password variables along with remaining context configs
        ### TODO 1 CODE START HERE
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
        ### TODO 1 CODE END HERE
    except Exception as e:
        logging.critical(f"Snowflake Authorization Context Handshake Failed: {str(e)}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # TODO 2: Semi-Structured Polymorphic Schema Verification (DDL) [RESOLVED]
    # Execute a DDL statement to guarantee the target landing table exists.
    # The table configuration MUST feature an active 'VARIANT' type data column 
    # to hold the raw unstructured polymorphic incoming document strings efficiently, 
    # alongside a default transactional generation record ingestion timestamp.
    # -------------------------------------------------------------------------
    try:
        ### TODO 2 CODE START
        cs.execute("""
            CREATE TABLE IF NOT EXISTS RAW_TRANSCRIPTS (
                json_payload VARIANT,
                inserted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        ### TODO 2 CODE END
    except Exception as e:
        logging.error(f"Failed to execute target structural validation DDL: {str(e)}")
        cs.close()
        ctx.close()
        sys.exit(1)

    # -------------------------------------------------------------------------
    # TODO 3: Safe Streaming Consumer Insertion Invariant [RESOLVED]
    # Process inputs infinitely line-by-line via sys.stdin streaming.
    # For every line:
    #   1. Clean trailing whitespace. Skip blank lines.
    #   2. Run structural sanity checks by deserializing the string to a dict.
    #   3. Build a parameterized injection-proof insertion template query.
    #   4. Convert the dict back into a serialized string literal and pass it
    #      safely inside a positional execution parameter tuple using PARSE_JSON(%s).
    # -------------------------------------------------------------------------
    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        try:
            # Safely validate structural correctness before invoking remote storage
            json_data = json.loads(cleaned_line)
            
            # Execute safe parameterized insertion. json.dumps() handles turning the
            # validated python dictionary cleanly back into a serialized string payload.

            ### TODO 3 CODE START
            insert_query = "INSERT INTO RAW_TRANSCRIPTS (json_payload) SELECT PARSE_JSON(%s)"
            cs.execute(insert_query, (json.dumps(json_data),))
            ### TODO 3 CODE END
            
            # Left intact from your original template design:
            logging.info(f"Loaded entry token item target: [{json_data.get('video_id', 'UNKNOWN')}] safely to warehouse.")
        except Exception as e:
            logging.error(f"Skipping corrupt pipeline payload stream element: {str(e)}")

    # -------------------------------------------------------------------------
    # TODO 4: Defensive Resource Reclamation Lifecycle [RESOLVED]
    # Ensure that resource cursors and connection pools are definitively closed 
    # out down to the operating system runtime container layout.
    # -------------------------------------------------------------------------
    ### TODO 4 CODE START
    cs.close()
    ctx.close()
    ### TODO 4 CODE END
    logging.info("Pipeline Step 3 finished execution cycles cleanly.")

if __name__ == '__main__':
    main()
    

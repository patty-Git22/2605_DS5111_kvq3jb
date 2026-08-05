{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS TECH_TERM,
    INSERTED_AT     AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }},
LATERAL FLATTEN(input => TECH_TERMS_ARRAY) f

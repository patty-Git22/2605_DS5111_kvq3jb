-- Master Pipeline Orchestrator
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09/transform/01_stg_youtube_transcripts.sql;
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09/transform/02_dim_videos.sql;
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09/transform/03_fct_entities.sql;

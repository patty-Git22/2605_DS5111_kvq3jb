-- Master Pipeline Orchestrator
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09_gitops_snowflake/transform/01_stg_youtube_transcripts.sql;
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09_gitops_snowflake/transform/02_dim_videos.sql;
EXECUTE IMMEDIATE FROM @DS5111_GIT_STAGE/branches/LAB09_gitops_snowflake/transform/03_fct_entities.sql;

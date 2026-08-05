{{ config(materialized='table') }}

-- 1. Define a Python-style list of core terms we want to track
{% set core_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    video_id,
    
    -- 2. Loop through the list to dynamically generate our columns
    {% for term in core_terms %}
    
    SUM(CASE WHEN LOWER(term_name) = '{{ term }}' THEN 1 ELSE 0 END) AS count_{{ term }}_mentions
    
    -- 3. Add a comma if it's not the last item in the loop
    {% if not loop.last %},{% endif %}
    
    {% endfor %}

FROM {{ ref('fct_tech_terms') }}
GROUP BY video_id

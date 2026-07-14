default:
	@cat makefile

env:
	python3 -m venv env; . env/bin/activate; pip install --upgrade pip

update: env
	. env/bin/activate; pip install -r requirements.txt

setup: update
	. env/bin/activate; pylint --generate-rcfile >> pylintrc

pipeline/logs:
	mkdir -p pipeline/logs

lint:
	. env/bin/activate; pylint bin/clean_ids.py
	. env/bin/activate; pylint bin/extract_transcripts.py

test: pipeline/logs lint
	. env/bin/activate; pytest -vv tests

test_enrich:
	@. env/bin/activate && cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py | python bin/validate_schema.py

.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | python bin/load_snowflake.py

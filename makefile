ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip

default:
	@cat makefile

env:
	python3 -m venv $(ENV)
	$(PIP) install --upgrade pip

update: env
	$(PIP) install -r requirements.txt

setup: update
	$(PYTHON) -m pylint --generate-rcfile >> pylintrc

pipeline/logs:
	mkdir -p pipeline/logs

lint:
	$(PYTHON) -m pylint bin/ tests/

test: pipeline/logs lint
	$(PYTHON) -m pytest -vv tests

test_enrich:
	cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) bin/validate_schema.py

run:
	$(PYTHON) bin/extract_transcripts.py
.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | $(PYTHON) bin/load_snowflake.py

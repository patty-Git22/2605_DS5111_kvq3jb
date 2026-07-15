# DS-5111_Software_And_Automation

## Project Core Objective

This repository implements a three-stage YouTube transcript pipeline:

1. **Extraction** (`bin/extract_transcripts.py`) — reads YouTube video IDs from
   stdin, fetches each raw transcript via the YouTube Transcript API (routed
   through a Webshare residential proxy when credentials are configured), and
   emits one JSON Lines record per video to stdout.
2. **Enrichment** (`bin/enrich_transcripts.py`) — reads raw transcript JSON
   Lines from stdin, sends each through the Gemini API for cleaning/annotation
   under a strict schema contract, and emits enriched JSON Lines to stdout.
3. **Validation** (`bin/validate_schema.py`) — reads enriched JSON Lines from
   stdin and verifies each record against the pipeline's data contract,
   exiting non-zero on any schema violation.

All stages communicate via stdin/stdout JSON Lines, so they can be piped
together (see `make test_enrich` in the Makefile). Logs from extraction and
enrichment are written to `pipeline/logs/pipeline_audit.log`.

## Environment Configuration Variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes (for enrichment stage) | Authenticates requests to the Gemini API |
| `WEBSHARE_USER` | No | Webshare proxy username; if unset, extraction runs with direct/unproxied requests |
| `WEBSHARE_PASSWORD` | No | Webshare proxy password; required alongside `WEBSHARE_USER` to enable proxy routing |

All variables are read from a local `.env` file (via `python-dotenv`) and are
never committed to version control — `.env` is excluded via `.gitignore`.

## Verification Steps

```bash
make lint     # runs pylint across bin/ and tests/
make test     # runs the full pytest suite (creates pipeline/logs/ if missing)
```

A fully configured environment should show `make lint` and `make test`
exiting with status 0 and no errors. CI runs both checks automatically as
parallel GitHub Actions jobs across Python 3.11–3.13 on every push and PR
to `main`.

## Requirements

* Log into AWS and set up a VM
* Make sure to select `Ubuntu Server 26.04`
* Get SSH key and link to personal Git repo.

## Automating init and setting up virtual environment

### Step 1: Automating the sequence to recreate VM

1. To avoid cloud instance crashes, create an `init.sh` file by typing `nano init.sh` in the root directory.
2. Within the `init.sh` file, copy and paste the following:
   - `sudo apt update` # To bring VM snapshot up to date with package versions
   - `sudo apt install make -y` # so we can use makefiles
   - `sudo apt install python3.14-venv -y` # so we can create python virtual environments
   - `sudo apt install tree` # a useful tool for listing files in tree form
3. Save and exit. Then type `chmod +x init.sh` to make it executable, followed by `bash init.sh` to run the file.
4. To confirm everything ran correctly, execute `tree`, which will show the file layout including `init.sh`.

### Step 2: GitHub Credential Setup

In order for GitHub to recognize who is issuing commits and pushes, we set up a configuration script to make this easily repeatable.

1. Create an `init_git_creds.sh` file using `nano` like before, and paste the following into it:

```bash
#!/usr/bin/bash

USER=<your github email>
NAME=<your github user name>

git config --global --list

git config --global user.email ${USER}
git config --global user.name  ${NAME}

git config --global --list
```

2. Replace `<your github email>` with the email associated with your GitHub account. Remove the `<>` as they are not needed.
3. Repeat that step by inserting your GitHub account name on the `NAME = ` line.
4. Exit and save. Then run the script using the same process as before:
   - Make it executable: `chmod +x init_git_creds.sh`
   - Run it: `bash init_git_creds.sh`

### Step 3: Clone Repo to the Machine

In order to save our work to our GitHub repo, we must first clone our repository.

1. Clone the repo using `git clone git@github.com:your_repo_name`, found by clicking the "Code" button, then the SSH option, on the repo's main page.
2. Move into the cloned repo using `cd <path name>`.
3. Create a new directory called `scripts` using `mkdir scripts`.
4. Move into the new directory: `cd scripts`.
5. Move your two init files into it:
   - `mv ~/init.sh .`
   - `mv ~/init_git_creds.sh .`
6. Add, commit, and push the files:
   - `git add .` (or add each file individually, e.g. `git add init.sh`)
   - `git commit -m "saving our two init files"`
   - `git push`
7. Confirm on GitHub that all files were pushed successfully.

### Step 4: Creating a Virtual Environment and Makefile for Repeatability

1. Navigate back to your root directory and create a file called `makefile`. The current version of this project's Makefile exposes the following targets:

```makefile
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
```

2. There is no need to make this file executable — it runs via the `make` command.
3. To confirm it's working, type `make` and you should see the contents of the file echoed to the console.
4. This project's actual `requirements.txt` includes the full dependency set needed for the pipeline, linting, and testing (see the file itself for the current pinned versions — it includes packages like `youtube-transcript-api`, `google-genai`, `python-dotenv`, `pylint`, and `pytest`, among others).
5. Run `make update` to install everything into the virtual environment.
6. Verify the environment is working:
   - `. env/bin/activate` — activate the environment (you should see `(env)` appear at the left of your prompt)
   - `pip list` — confirm the expected packages are installed
   - `make lint` and `make test` — confirm the codebase passes its quality gates
7. Push everything to your GitHub repo using the same add/commit/push commands as before.

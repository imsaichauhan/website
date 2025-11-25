# Scripts Directory

This directory contains automation scripts for the PROGRESS website.

## Available Scripts

### gen-bookmarks.sh
**Purpose:** Wrapper script to regenerate the bookmarks index page.

**Usage:**
```bash
_scripts/gen-bookmarks.sh
```

**What it does:**
- Runs `generate-bookmarks.py` with the correct Python interpreter
- Reads data from `_data/bookmarks.yml`
- Generates `bookmarks/index.qmd` with all bookmark cards

### generate-bookmarks.py
**Purpose:** Python script that generates the bookmarks index page from YAML data.

**Usage:**
```bash
# Via wrapper (recommended):
_scripts/gen-bookmarks.sh

# Direct (requires activated venv):
source .venv/bin/activate
python _scripts/generate-bookmarks.py
```

**Input:** `_data/bookmarks.yml`  
**Output:** `bookmarks/index.qmd`

**To add/edit bookmarks:**
1. Edit `_data/bookmarks.yml`
2. Run `_scripts/gen-bookmarks.sh`
3. Run `quarto render bookmarks/index.qmd`

### generate-projects.py
**Purpose:** Script for managing project pages (details TBD).

## Workflow

Typical workflow for updating bookmarks:

```bash
# 1. Edit the data file
nano _data/bookmarks.yml

# 2. Regenerate the index page
_scripts/gen-bookmarks.sh

# 3. Rebuild the site
quarto render
```

## Requirements

- Python 3.13+ with virtual environment at `../.venv/`
- PyYAML package installed in venv

### run.sh (single entrypoint)
**Purpose:** A single, convenient wrapper to run the common scripts from this folder.

**Usage:**

```bash
_scripts/run.sh bookmarks    # regenerate bookmarks/index.qmd
_scripts/run.sh projects     # regenerate projects/index.qmd
_scripts/run.sh images       # download bookmark images
_scripts/run.sh all          # bookmarks + projects
_scripts/run.sh help         # show this help
```

**Behavior and notes:**
- `run.sh` will prefer the repo virtualenv at `./.venv/bin/python` when present.
- If wrappers like `gen-bookmarks.sh` or `gen-projects.sh` are executable they will be used; otherwise `run.sh` falls back to calling the Python scripts directly.
- Use `./_scripts/run.sh bookmarks && quarto render` as a short workflow to regenerate and rebuild.

### Making scripts easy to run
- Ensure scripts are executable:

```bash
chmod +x _scripts/*.sh _scripts/*.py
```

- Recommended quick setup for Python dependencies (one-time):

```bash
python3 -m venv .venv
.venv/bin/pip install -r _scripts/requirements.txt  # create this file with pyyaml if you like
```

If you want, I can add a `requirements.txt` and a top-level `Makefile` to make the workflow even simpler.

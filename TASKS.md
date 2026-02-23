# Xether AI CLI - Progress Tracking

This document tracks the progress of the Xether AI command-line interface (CLI) tool. The CLI is designed to provide developers and data engineers with an efficient way to interact with the platform directly from their terminal.

**Technology Stack**: Python, [Typer](https://typer.tiangolo.com/) (CLI framework), [Rich](https://rich.readthedocs.io/) (for beautiful terminal formatting), [HTTPX](https://www.python-httpx.org/) (for async/sync HTTP client communication with the Main Backend).

---

## 📊 Phase Status Overview

| Phase | Title                        | Status     | Progress |
| :---- | :--------------------------- | :--------- | :------- |
| 1     | Project Setup & Architecture | ⏳ Pending | 0%       |
| 2     | Core Infrastructure & Auth   | ⏳ Pending | 0%       |
| 3     | Dataset Management commands  | ⏳ Pending | 0%       |
| 4     | Pipeline Management commands | ⏳ Pending | 0%       |
| 5     | Artifact Operations          | ⏳ Pending | 0%       |
| 6     | Distribution & Polish        | ⏳ Pending | 0%       |

---

## ⏳ Phase 1 — Project Setup & Architecture `PENDING`

**Goal**: Initialize the Python project and establish a clean, scalable directory structure for the CLI.

- [ ] Initialize Python environment (using Poetry or standard `pip`/`venv`).
- [ ] Install base dependencies: `typer`, `rich`, `httpx`, `pydantic`.
- [ ] Define project structure (e.g., `src/xether_cli/`, `commands/`, `core/`, `api/`).
- [ ] Set up the main CLI entry point (`xether`).
- [ ] Configure `pyproject.toml` or `setup.py` with an entry point (`xether = xether_cli.main:app`).
- [ ] Add basic test boilerplate (`pytest`).

---

## ⏳ Phase 2 — Core Infrastructure & Auth `PENDING`

**Goal**: Implement the API client, local configuration management, and the authentication flow (`login` / `logout`).

- [ ] Implement `xether.api.client` using `httpx` with predefined `Main Backend` URLs (via environment variable or config).
- [ ] Implement local configuration management (save API keys/tokens to `~/.xether/config.json` or `~/.config/xether/`).
- [ ] Implement `xether login` command (prompt for user credentials/API token and store session).
- [ ] Implement `xether logout` command (clear local session).
- [ ] Implement `xether config set` and `xether config view` to manage backend endpoint URLs (e.g., setting the target backend URL for local vs prod).
- [ ] Create `Rich` output formatting utilities (spinners, styled success/error messages).

---

## ⏳ Phase 3 — Dataset Management `PENDING`

**Goal**: Allow users to manipulate and inspect datasets via the CLI.

- [ ] Implement `xether dataset ls` (fetch and display datasets in a Rich table).
- [ ] Implement `xether dataset info [DATASET_ID]` (fetch detailed dataset metadata).
- [ ] Implement `xether dataset push [FILE_PATH]` (upload a dataset).
  - _Note: Needs to request a pre-signed URL from Backend, then execute an S3/MinIO upload locally with a progress bar._
- [ ] Implement `xether dataset rm [DATASET_ID]` (delete dataset and its associated binary blob).

---

## ⏳ Phase 4 — Pipeline Orchestration `PENDING`

**Goal**: Provide commands to trigger and monitor analytical/transformation pipelines.

- [ ] Implement `xether pipeline ls` (list available pipelines).
- [ ] Implement `xether pipeline run [PIPELINE_ID]` (trigger a new pipeline execution).
  - _Options to pass pipeline parameters via flags or a JSON file._
- [ ] Implement `xether pipeline status [EXECUTION_ID]` (check the real-time status of a pipeline run).
- [ ] Implement `xether pipeline history [PIPELINE_ID]` (list previous executions of a specific pipeline).

---

## ⏳ Phase 5 — Artifact Operations `PENDING`

**Goal**: Enable downloading and inspecting resultant artifacts from pipeline runs.

- [ ] Implement `xether artifact ls` (list artifacts, potentially filtered by pipeline execution ID).
- [ ] Implement `xether artifact download [ARTIFACT_ID] [DESTINATION_PATH]` (download artifact output).
  - _Note: Ensure it fetches pre-signed download URLs from the Artifact Storage service via Backend._
- [ ] Verify checksums (SHA-256) upon downloading an artifact.

---

## ⏳ Phase 6 — Distribution & Polish `PENDING`

**Goal**: Get the CLI ready for developers to install and use easily.

- [ ] Add extensive help text and examples to all commands (visible via `xether --help`).
- [ ] Implement structured error handling (graceful exits on 401s, 403s, 500s from the Main Backend).
- [ ] Finalize `README.md` with installation and quickstart guides.
- [ ] Setup GitHub Actions CI to build and test the CLI.
- [ ] (Optional) Package for PyPI (`pip install xether-cli`) and Homebrew.

---

_Created: 2026-02-23 - Initial project scaffolding mapped._

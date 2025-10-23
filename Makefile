# ====== Project Vars ======
PY        ?= python3
PIP        = $(VENV)/bin/pip
RUN        = $(VENV)/bin/python
VENV      ?= .venv
THREAD    ?= mf-demo-001
BRIEF     ?= Write a night-train rock ballad with wet asphalt and a hard choice.
FEEDBACK  ?=
MODEL_ENV ?= .env

# ====== Help ======
.PHONY: help
help:
	@echo "Targets:"
	@echo "  venv              Create a virtualenv (.venv)"
	@echo "  install           Install dependencies into .venv"
	@echo "  kb-index          Build Prosody KB index (Chroma)"
	@echo "  memory-index      Build User Memory index (Chroma)"
	@echo "  ensure-stores     Build both indexes if missing/empty"
	@echo "  run-demo          Run legacy demo graph"
	@echo "  run-mf            Run Memory-Fueled PaE graph (A/B context). THREAD, BRIEF, FEEDBACK vars supported"
	@echo "  test              Run tests"
	@echo "  clean             Remove caches/compiled artifacts"
	@echo "  dc-build/up/down  Docker Compose build/up/down"
	@echo "  dc-mf             Run Memory-Fueled graph in Docker (use BRIEF/FEEDBACK/THREAD env or make vars)"
	@echo ""
	@echo "Examples:"
	@echo "  make run-mf THREAD=mf-01 BRIEF='Ballad about broken neon and rain' "
	@echo "  make run-mf THREAD=mf-01 FEEDBACK='A; faster tempo; add image: neon puddles'"
	@echo "  make dc-mf THREAD=mf-01 BRIEF='...'"

# ====== Local Dev ======
$(VENV):
	$(PY) -m venv $(VENV)

.PHONY: venv
venv: $(VENV)

.PHONY: install
install: venv
	. $(VENV)/bin/activate && pip install --upgrade pip
	$(PIP) install -r requirements.txt

# ====== Indexing ======
.PHONY: kb-index
kb-index: install
	$(RUN) app/indexing/build_kb_index.py --source kb/prosody_corpus --persist vectorstores/prosody --collection prosody

.PHONY: memory-index
memory-index: install
	$(RUN) app/indexing/build_memory_index.py --memory memory --persist vectorstores/memory --collection memory

.PHONY: ensure-stores
ensure-stores: install
	@$(PY) - <<'PYCODE'
from pathlib import Path
import subprocess, sys
def empty(p): 
    return (not p.exists()) or (not any(p.iterdir()))
if empty(Path("vectorstores/prosody")):
    print("[INIT] Building Prosody KB index...")
    subprocess.check_call([sys.executable, "app/indexing/build_kb_index.py", "--source","kb/prosody_corpus","--persist","vectorstores/prosody","--collection","prosody"])
if empty(Path("vectorstores/memory")):
    print("[INIT] Building User Memory index...")
    subprocess.check_call([sys.executable, "app/indexing/build_memory_index.py", "--memory","memory","--persist","vectorstores/memory","--collection","memory"])
print("[OK] Vectorstores ready.")
PYCODE

# ====== Run Scripts ======
.PHONY: run-demo
run-demo: install ensure-stores
	$(RUN) scripts/run_demo.py

.PHONY: run-mf
run-mf: install ensure-stores
	@if [ -n "$(FEEDBACK)" ]; then \
	  $(RUN) scripts/run_memory_fueled.py --thread-id "$(THREAD)" --feedback "$(FEEDBACK)" --print-state ; \
	else \
	  $(RUN) scripts/run_memory_fueled.py --thread-id "$(THREAD)" --brief "$(BRIEF)" --print-state ; \
	fi

# ====== Tests & Cleaning ======
.PHONY: test
test: install
	$(VENV)/bin/python -m pytest -q

.PHONY: clean
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -name '*.pyc' -delete

# ====== Docker Compose ======
.PHONY: dc-build
dc-build:
	docker compose build

.PHONY: dc-up
dc-up:
	docker compose up -d

.PHONY: dc-down
dc-down:
	docker compose down

.PHONY: dc-logs
dc-logs:
	docker compose logs -f app

# Run Memory-Fueled graph inside Docker
.PHONY: dc-mf
dc-mf:
	@if [ -n "$(FEEDBACK)" ]; then \
	  docker compose run --rm -e OPENAI_API_KEY -e PYTHONUNBUFFERED=1 app bash -lc \
	    "pip install -r requirements.txt && python scripts/run_memory_fueled.py --thread-id '$(THREAD)' --feedback '$(FEEDBACK)' --print-state"; \
	else \
	  docker compose run --rm -e OPENAI_API_KEY -e PYTHONUNBUFFERED=1 app bash -lc \
	    "pip install -r requirements.txt && python scripts/run_memory_fueled.py --thread-id '$(THREAD)' --brief '$(BRIEF)' --print-state"; \
	fi

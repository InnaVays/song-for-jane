# ====== Project Vars ======
PY        ?= python3
VENV      ?= .venv
PIP        = $(VENV)/bin/pip
RUN        = $(VENV)/bin/python
THREAD    ?= mf-demo-001
BRIEF     ?= Write a night-train rock ballad with wet asphalt and a hard choice.
FEEDBACK  ?=
MODEL_ENV ?= .env

# ====== Help ======
.PHONY: help
help:
	@echo "Targets:"
	@echo "  venv              Create a virtualenv (.venv)"
	@echo "  install           Install dependencies"
	@echo "  kb-index          Build Prosody KB index (Chroma)"
	@echo "  memory-index      Build User Memory index (Chroma)"
	@echo "  ensure-stores     Build both indexes if missing/empty"
	@echo "  run-demo          Run legacy demo graph"
	@echo "  run-mf            Run Memory-Fueled PaE graph (A/B context)"
	@echo "  test              Run tests"
	@echo "  clean             Remove caches/compiled artifacts"
	@echo "  dc-build/up/down  Docker Compose build/up/down"
	@echo "  dc-mf             Run Memory-Fueled graph in Docker"

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

.PHONY: dc-ensure-stores
dc-ensure-stores:
	docker compose exec app bash -lc "\
	  if [ ! -d vectorstores/prosody ] || [ -z \"$$ (ls -A vectorstores/prosody 2>/dev/null)\" ]; then \
	    echo '[INIT] Building Prosody KB index...'; \
	    python app/indexing/build_kb_index.py --source kb/prosody_corpus --persist vectorstores/prosody --collection prosody; \
	  fi; \
	  if [ ! -d vectorstores/memory ] || [ -z \"$$ (ls -A vectorstores/memory 2>/dev/null)\" ]; then \
	    echo '[INIT] Building User Memory index...'; \
	    python app/indexing/build_memory_index.py --memory memory --persist vectorstores/memory --collection memory; \
	  fi; \
	  echo '[OK] Vectorstores ready.'"

# ====== Run Scripts ======
.PHONY: run-demo
run-demo: install ensure-stores
	$(RUN) scripts/run_demo.py

.PHONY: run-mf
run-mf: install ensure-stores
	@if [ -n "$(FEEDBACK)" ]; then \
	  $(RUN) scripts/run_demo.py --thread-id "$(THREAD)" --feedback "$(FEEDBACK)" --print-state ; \
	else \
	  $(RUN) scripts/run_demo.py --thread-id "$(THREAD)" --brief "$(BRIEF)" --print-state ; \
	fi

# ====== Tests & Cleaning ======
.PHONY: test
test: install
	$(VENV)/bin/python -m pytest -q || true

.PHONY: clean
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -name '*.pyc' -delete

# ====== Docker Compose ======
.PHONY: dc-build
dc-build:
	docker compose build

.PHONY: dc-install
dc-install:
	docker compose exec app bash -lc "pip install --no-cache-dir -r requirements.txt"

.PHONY: dc-up
dc-up:
	docker compose up -d

.PHONY: dc-down
dc-down:
	docker compose down

.PHONY: dc-logs
dc-logs:
	docker compose logs -f app

.PHONY: dc-mf
dc-mf:
	@if [ -n "$(FEEDBACK)" ]; then \
	  docker compose exec app bash -lc "\
	    python scripts/run_demo.py --thread-id '$(THREAD)' --feedback '$(FEEDBACK)' --print-state"; \
	else \
	  docker compose exec app bash -lc "\
	    python scripts/run_demo.py --thread-id '$(THREAD)' --brief '$(BRIEF)' --print-state"; \
	fi
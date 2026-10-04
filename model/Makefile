# P1 data/ML: heating + cooling (H+C) estimates.
# Run from the repo root with:  make -C model <target>     (or `cd model && make <target>`)
#
#   make -C model dashboard   start the heating/cooling API + explorer UI → http://localhost:8001/dashboard
#   make -C model stop        stop it
#   make -C model setup       create .venv and install requirements
#   make -C model build       rebuild every dataset, model and validation result (cached downloads)
#   make -C model test        run the tests

ROOT    := $(abspath $(CURDIR)/..)
VENV    := $(ROOT)/.venv
PY      := $(VENV)/bin/python
PORT    ?= 8001
# The heating/cooling estimate server (FastAPI). It only serves heating + cooling data:
# /hc/estimate, /hc/weather, /hc/bill_check, /hc/buildings, /hc/validation, /dashboard
HC_SERVER := model.heating_cooling.server:app

.PHONY: dashboard serve stop setup build test help

help:
	@sed -n '1,9p' Makefile

dashboard: serve

serve: $(PY)
	@echo "Heating + cooling explorer → http://localhost:$(PORT)/dashboard   (API docs: /docs; Ctrl-C to stop)"
	cd $(ROOT) && $(PY) -m uvicorn $(HC_SERVER) --port $(PORT)

stop:
	-@pkill -f "uvicorn $(HC_SERVER)" && echo "stopped heating/cooling server" || echo "heating/cooling server not running"

setup $(PY):
	python3 -m venv --system-site-packages $(VENV)
	$(VENV)/bin/pip install -q -r $(ROOT)/model/requirements.txt

build: $(PY)
	cd $(ROOT) && $(PY) -m model.scripts.build_all

test: $(PY)
	cd $(ROOT) && $(PY) -m pytest model/tests -q

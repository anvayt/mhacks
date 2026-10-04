.PHONY: install deps data data-bundle gis model demo demo-public demo-public-check demo-warm demo-warm-city demo-check phase2-check

# One-step setup. Each step is skipped when its output already exists:
#   deps  -> .venv, api/.venv, web/ and agent/ node_modules
#   data  -> unzips model-data.zip from the repo root, if present, so gis/model skip downloads and training
#   gis   -> data/a2_footprints.geojson, data/a2_mailing_addresses.geojson
#   model -> model/artifacts/resstock_hc.pkl (first build downloads ~1 h of data)
MODEL_PKL  := model/artifacts/resstock_hc.pkl
MODEL_TABLE := model/data/processed/buildings_hc.parquet

install: deps data gis model

deps:
	@bash scripts/install.sh

data:
	@if [ -f model-data.zip ]; then bash scripts/model-data.sh unpack; \
	else echo '==> data: no model-data.zip in repo root; missing inputs will be downloaded'; fi

# Zip this checkout's downloaded data and trained model into model-data.zip to share with teammates.
data-bundle:
	@bash scripts/model-data.sh pack

gis: deps data
	@if [ -s data/a2_footprints.geojson ] && [ -s data/a2_mailing_addresses.geojson ]; then \
		echo '==> gis: footprints already downloaded'; \
	else \
		echo '==> gis: downloading Ann Arbor footprints (~30 s)'; \
		cd api && .venv/bin/python scripts/fetch_footprints.py; \
	fi

model: deps data
	@if [ -f $(MODEL_PKL) ] && [ -f $(MODEL_TABLE) ]; then \
		echo '==> model: already built ($(MODEL_PKL))'; \
	else \
		echo '==> model: building (first run downloads ~1 h of data)'; \
		$(MAKE) -C model build; \
	fi

demo:
	@bash scripts/demo.sh

demo-public:
	@bash scripts/demo-public.sh

demo-public-check:
	@bash scripts/demo-public-check.sh

demo-warm:
	@bash scripts/demo-warm.sh

demo-warm-city:
	@bash scripts/demo-warm-city.sh

demo-check:
	@bash scripts/demo-check.sh

phase2-check:
	@bash scripts/phase2-e2e.sh

.PHONY: demo-video
demo-video:
	@bash demo/video/run.sh $(VIDEO_ARGS)

.PHONY: asi-agent asi-agent-test
ASI_ENV_FILE ?= /Users/anvaytodkar/Code/mhacks/.env
asi-agent:
	@uv run --project asi-agent --env-file "$(ASI_ENV_FILE)" python asi-agent/agent.py

asi-agent-test:
	@uv run --project asi-agent pytest asi-agent/tests -q

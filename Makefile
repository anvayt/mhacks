.PHONY: install deps gis model demo demo-public demo-public-check demo-warm demo-warm-city demo-check phase2-check

# One-step setup. Each step is skipped when its output already exists:
#   deps  -> .venv, api/.venv, web/ and agent/ node_modules
#   gis   -> data/a2_footprints.geojson, data/a2_mailing_addresses.geojson
#   model -> model/artifacts/resstock_hc.pkl (first build downloads ~1 h of data)
MODEL_PKL  := model/artifacts/resstock_hc.pkl

install: deps gis model

deps:
	@bash scripts/install.sh

gis: deps
	@if [ -s data/a2_footprints.geojson ] && [ -s data/a2_mailing_addresses.geojson ]; then \
		echo '==> gis: footprints already downloaded'; \
	else \
		echo '==> gis: downloading Ann Arbor footprints (~30 s)'; \
		cd api && .venv/bin/python scripts/fetch_footprints.py; \
	fi

model: deps
	@if [ -f $(MODEL_PKL) ]; then \
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

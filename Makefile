.PHONY: demo demo-public demo-public-check demo-warm demo-warm-city demo-check phase2-check

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

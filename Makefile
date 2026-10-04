.PHONY: demo demo-public demo-warm demo-check phase2-check

demo:
	@bash scripts/demo.sh

demo-public:
	@bash scripts/demo-public.sh

demo-warm:
	@bash scripts/demo-warm.sh

demo-check:
	@bash scripts/demo-check.sh

phase2-check:
	@bash scripts/phase2-e2e.sh

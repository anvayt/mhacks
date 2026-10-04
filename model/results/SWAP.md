# Manual P1 model swap / rollback — lead only

**These are handoff instructions, not actions performed by the P1 finishing task.** The live `mhacks-integration` checkout and service on port 8001 were not changed. The tested replacement is `/Users/anvaytodkar/Code/mhacks-p1` on `p1/finish`, using a copy of the live built artifacts and matching Python environment. No model build or global stop command is needed.

Before switching, the production API must run the new merged `dev` code (with its existing APP_DB, SESSIONS_DB, CALIBRATE_DB, allowed origins and credentials). The new capability client is API code; replacing only the model cannot add it to an already running old API. Do not point the production API at the scratch databases used in this task. There is no data/schema migration in this change. Once the updated API is running, capability discovery refreshes within 30 seconds; no further API restart is needed for the model swap or rollback.

## Swap model

1. In the existing **model-only** terminal, press Ctrl-C to stop that model process. Do not stop a terminal running the entire demo launcher: it may own other services. If that terminal is unavailable, inspect the one listener and its working directory, then terminate only that PID:

   ```bash
   MODEL_PID=$(lsof -nP -iTCP:8001 -sTCP:LISTEN -t | sort -u)
   test -n "$MODEL_PID" && test "$(printf '%s\n' "$MODEL_PID" | wc -l | tr -d ' ')" = 1
   ps -p "$MODEL_PID" -o pid=,command=
   lsof -a -p "$MODEL_PID" -d cwd
   # Proceed only after confirming this is the intended live model process.
   kill -TERM "$MODEL_PID"
   ```

   Confirm the port is released (`lsof -nP -iTCP:8001 -sTCP:LISTEN` should return no listener). Do not use `make -C model stop`, pkill, or any demo-stack launcher.

2. In a dedicated model-only terminal, start the prepared replacement in the foreground:

   ```bash
   cd /Users/anvaytodkar/Code/mhacks-p1
   .venv/bin/python -m uvicorn model.heating_cooling.server:app --host 127.0.0.1 --port 8001
   ```

   Use `python -m uvicorn`: the copied venv's uvicorn console-script shebang may still name the old checkout. The artifacts and caches already exist; **do not rebuild**.

3. From another terminal, verify capabilities and the same Morton gas/single-pane scenario that passed acceptance:

   ```bash
   curl -fsS http://localhost:8001/hc/capabilities
   curl -fsS 'http://localhost:8001/hc/estimate?lat=42.262408681964544&lon=-83.7283761815115&unit_sqft=2753&building_type=Single-Family%20Detached&block_group=261614004003&heating_fuel=gas&window_panes=1'
   ```

   Expect capabilities to list the five effects, `lookalikes`, and `within_building`; the unmodified scenario's `annual.total_usd` is **2185** in the recorded copied-artifact test. Then verify the API `/commitments/suggested?session_id=...` prices supported gas actions and `/map/{session_id}` has peer counts in `steps[].lookalikes`. A fresh API estimate is appropriate if the user changes answers; projections must not replace the current estimate.

4. Rewarm through the API, without launching the demo stack or managing the model:

   ```bash
   cd /Users/anvaytodkar/Code/mhacks-p1
   API_BASE_URL=http://localhost:8000 uv run --env-file /Users/anvaytodkar/Code/mhacks/.env --project api make demo-warm
   ```

   This calls the existing API for five estimates, maps, forecasts and the city layer. Any unrelated external-weather failure must be reported, not treated as successful warming. Do not print `.env` or pass keys as command-line literals.

## Rollback model

Stop only the replacement model with Ctrl-C in its dedicated terminal (or identify and verify its single port-8001 PID as above). Start the unchanged prior checkout:

```bash
cd /Users/anvaytodkar/Code/mhacks-integration
.venv/bin/python -m uvicorn model.heating_cooling.server:app --host 127.0.0.1 --port 8001
```

`curl -fsS http://localhost:8001/hc/answers` verifies readiness. `/hc/capabilities` returning 404 is expected for the old server. Within 30 seconds the updated API falls back to its old placeholder effects, old bill-noise behavior and honest empty peer clouds. Existing sessions/bills/grades are retained; rollback does not undo saved hypothetical projections or bill records. Re-run the same `make demo-warm` command through the API. No checkout reset, force push, artifact deletion or database replacement is needed.

## Evidence

- `finish/compatibility.json`: 75/75 legacy numeric-token comparisons match (5 demo addresses + 20 sampled footprints × 3 endpoints).
- `finish/api_tests.log`, `finish/model_tests.log`, `finish/phase2.log`: automated checks.
- `finish/live_smoke.json`: exact isolated live examples; hypothetical typed bill explicitly labeled.
- `SIGNOFF.md`: copied artifact hashes, runtime versions, regenerated validation and the corrected **29.2% blend** headline.

New effects are stock-based projected scenarios; metered/electric envelope effects remain placeholders. The temporal noise floor is not a claim of improved cross-building accuracy or proof of causal savings. The approved heat-pump dollar-composition exception is documented in `EFFECTS.md` and `../research/P1_FINISH.md`. Nothing here changes baseline city scores.

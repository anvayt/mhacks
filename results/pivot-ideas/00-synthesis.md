# Pivot Ideas — Synthesis

Four researchers worked in parallel (past-winner patterns, sponsor stack, sustainability impact, demo-first). Each read the 2020–2025 winner research and proposed 3 ideas that are **not** appliance scheduling. Full write-ups: `01-past-winner-patterns.md`, `02-sponsor-stack.md`, `03-sustainability-impact.md`, `04-demo-first.md`.

## Convergence
3 of 4 researchers independently picked the same concept as their top idea: **Fern as a climate-emergency check-in line for people at risk** ("Fern on Call" from the sponsor-stack and sustainability scouts, "Smoke Signal" from the demo-first designer). The past-winner miner's pick was different: "Hold the Line", a FinTech scam interceptor.

## Ranked top 3

### 1. Fern on Call: heat and smoke check-ins (Sustainability, framed as climate resilience)
GOES-19 smoke/heat data plus NOAA's smoke forecast tell Fern when a heat wave or wildfire smoke is about to hit where someone vulnerable lives. Her FREE-WILi "pot" on their table lights up and asks them, in her voice, to press the button (or tip it like watering) to say they're OK. If they don't respond, Fern video-calls their family in Relay and works down the contact list until a human has checked in.
- **Sponsors, all doing core work:** SpaceX (satellite data sets the risk), Relay (escalation calls), ElevenLabs (the voice *is* the interface), FREE-WILi (the no-app endpoint; no IR appliance needed), Fetch.ai (caregiver setup via ASI:One). FinchNode and Figma are optional.
- **Fun track:** Judged by an LLM.
- **Reuse:** about 50–65%. Fern's wilted/normal/blooming moods map onto bad/okay/clean-air days, her voice and HD loops carry over, the GOES-19 plan swaps product, and the Relay plan carries over. No new xAI spend needed.
- **Why it can win:** named vulnerable user plus a statistic plus a Michigan hook (P2 from the past-winner research; heat is the deadliest US weather hazard, and Wayne County had 16 smoke alert days by Aug 2025). An agent that escalates text → call like F.L.U.D.D (2021 winner). A physical object the judge interacts with, like Wattson (2025 Sustainability winner).
- **Risks:** "elder check-in" has won at MHacks before (CogniCare, Dementia Assistant), so lead with the climate/satellite trigger. There's no live hazard in Michigan this weekend, so the drama is a labeled replay of a real archived event (Jul 31, 2025 Detroit smoke), plus live western-US smoke for proof it's real-time. It's adaptation rather than mitigation, so say "climate resilience" early. Relay calls may not work on the public app build (fallback: Relay text + voice notes, or Photon).
- **Optional merge from "Tend":** check in by tipping the FREE-WILi like a watering can (accelerometer). Accelerometer builds won FREE-WILi's prize three times.

### 2. Hold the Line: elder scam interceptor (FinTech)
Fern watches Grandma's Capital One Nessie account. When a payment looks like a scam ("grandson in jail", gift cards, rushed wire), she holds it as pending, asks Grandma for the family safe word, and texts then video-calls the trusted grandkid in Relay before any money leaves.
- **Strengths:** hits the most proven winning patterns; no MHacks winner has done scam interception; direct evidence Capital One judges reward fraud + voice on Nessie (ZenStock MHacks 16, HR Audit HackGT 12); feasibility 8/10; the judge plays the scammer.
- **Costs:** FinTech main track (the team leaned away from it), no space data, so the SpaceX track is lost, and the FREE-WILi becomes optional.

### 3. Sprout: physical-therapy rep counter (Hardware)
A FREE-WILi strapped to the forearm measures home-exercise reps and range of motion; Fern counts out loud, blooms as numbers improve, calls you in Relay when you skip, and reports to your PT. Strong demo (the judge does wrist curls), but it depends on the untested FREE-WILi motion stream, and accelerometer wearables (Gestura, ScreenWave) already won in 2025.

## Recommendation
**Fern on Call.** It's the independent consensus, it's clearly not niche, it uses every core sponsor for real, it reuses the most of what's already built, and it solves the "we have no IR appliance" problem: the FREE-WILi itself becomes the product's endpoint.

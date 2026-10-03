# SpaceX: Make it Legendary

**Prize:** SpaceXAI mechanical keyboards (one team), plus a bottle raffle for all entrants.
**Competition:** medium; many entries, few actually built around space data.

## Rules
- "Real space data goes in"
- **Must be built with Cursor**; more Cursor use = better odds
- **Must use the Grok Imagine or Grok Voice API**
- Bonus: use Grok Bot for planning

## What we use
- **Space data:** GOES-19 satellite sunlight + cloud data (drives the forecast)
- **Backup space data:** GOES-19 orbit from CelesTrak, in case Earth-observation data doesn't count
- **Grok Imagine:** garden visuals (label as AI illustrations)
- **Grok Voice:** the agent's voice
- **Cursor:** everyone codes in it; commit `.cursor/rules`; screenshot agent sessions for Devpost

## Setup
- xAI account at console.x.ai; no free tier. Worst case ~$15 total. Ask for credits at the Expo/booth
- API is OpenAI-compatible at `https://api.x.ai/v1`
- Grok Voice: `wss://api.x.ai/v1/realtime`. Use ephemeral tokens in the browser

## Watch out
- Ask at the Expo whether satellite weather data counts as "space data"
- The r/SpaceX API is dead
- CelesTrak bans repeat downloads; download once and cache

**Time:** about 5 hours.
**Events:** Grok photo booth Sat 2–6 PM (Atrium) · SpaceXAI session Sat 4–5 PM (VR Lab) · coffee cart Sun 9 AM (BBB).

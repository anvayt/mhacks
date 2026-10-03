# Clean Hours: MHacks 2026

**Deadline: Sun 12:00 PM. Judging: Sun 12:30–3:00 PM, Duderstadt Basement, 3-min pitch at the table.**

## Tracks
- **Main:** Sustainability
- **Sponsors:** FREE-WILi, SpaceX "Make it Legendary", SpacetimeDB
- **Fun:** Judged by an LLM only (free; it scores the Devpost write-up we're writing anyway)

## What it is
An agent that picks the cleanest hour to use electricity, then flips real devices on or off.
- Reads live Midwest grid carbon data and GOES-19 satellite sunlight/cloud data.
- Forecasts the cleanest hour today (sunny → noon is cleanest; cloudy → 3 AM).
- A voice agent tells you when to run the dryer, and you confirm by voice.
- **Auto mode** (opt-in): when the grid hits a dirty peak, the agent switches registered devices off itself via FREE-WILi infrared.
- Shared **Digital Garden**: your floor's garden grows with every gram of CO₂ saved, live on everyone's phone.

## How each sponsor is used
| Sponsor | What we build |
|---|---|
| **FREE-WILi** | Learns a fan's IR remote code and switches it on or off; shows the garden on its screen/LEDs; physical "I'm leaving" button turns everything off |
| **SpaceX** | GOES-19 satellite data drives the forecast. Built in Cursor (required). Agent voice via Grok Voice; garden visuals via Grok Imagine (one is required) |
| **SpacetimeDB** | Real-time backend for the shared garden: players, floors, devices, saved CO₂. Judges scan a QR code and join live |

## Team
| Person | Owns |
|---|---|
| P1 | SpacetimeDB + web app (garden, QR join) |
| P2 | Satellite + grid data, forecast; goes to SpaceXAI session 4 PM |
| P3 | Voice agent (Grok Voice/Imagine), auto mode, Devpost write-up, demo video |
| P4 | FREE-WILi + IR; goes to FREE-WILi session 1 PM; leads pitch |

Everyone codes in **Cursor** (SpaceX requirement).

## Schedule
| Time | Checkpoint | If it fails |
|---|---|---|
| 11:30 Expo | Ask SpaceXAI: does satellite weather data count as "space data"? Credits? Ask FREE-WILi: loaner kits? Which library? | No loaners → fake on-screen device |
| 12:00 | Hacking starts. Repo, API keys, Devpost skeleton | — |
| 2:00 PM | FREE-WILi blinks LEDs and switches the fan via IR | Use simulated device, keep going |
| 3:00 PM | Satellite sunlight value for Ann Arbor looks right | Use cloud mask instead |
| 4:00 PM | SpaceXAI session confirms the data rule | If no → drop SpaceX, keep the project |
| 6:00 PM | 2+ phones see the garden update live | Simplify to one shared garden |
| Midnight | Full loop works: forecast → voice agent → fan → garden grows | Cut all extras, everyone on the core |
| 6 AM | Freeze UI | — |
| 11 AM | Devpost submitted | — |

**Cut first if behind:** extras → Grok Imagine visuals (keep Voice) → floor leaderboard → auto mode.
**Never cut:** satellite data in the forecast, the fan switching, the CO₂ number, live sync.

## Tech
- **Backend:** Python (FastAPI) for forecast, satellite, and FREE-WILi control
- **Database:** SpacetimeDB (TypeScript module) on Maincloud
- **Frontend:** React web app
- **Satellite data (free, no key):**
  - Sunlight: `noaa-goes19` S3 bucket, `ABI-L2-DSRF` (every 10 min, daytime only)
  - Clouds: `ABI-L2-ACMC` (every 5 min)
  - Live image: `cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/cgl/GEOCOLOR/1200x1200.jpg`
- **Grid data:** Electricity Maps (zone `US-MIDW-MISO`, free key) + EIA-930 (14 days of history)
- **Cache satellite files hourly from 12–7 PM**; no sunlight data after sunset.

## Demo (3 min)
1. **0:00:** "Same electricity, different hour, different CO₂. The cleanest hour flips with the clouds."
2. **0:15:** Show the live satellite image and forecast: "cleanest window is now."
3. **0:35:** The agent asks: "Grid's at its cleanest today. Start the dryer?" Judge says yes, **the fan turns on**.
4. **1:15:** Judge scans the QR code, and the garden grows on every screen.
5. **1:45:** The tech: satellite → forecast → X% less CO₂ (backtested over 14 days).
6. **2:20:** Auto mode: show last night's real dirty peak (labeled as a replay), when the agent switched the fan off on its own, plus the CO₂ it saved.
7. **2:45:** Limitations + what's next.

Always keep 2 people at the table during judging.

## Before noon
- [ ] Buy/borrow a cheap IR fan or LED strip with remote
- [ ] Electricity Maps + EIA API keys
- [ ] xAI console account (ask for credits at Expo)
- [ ] `spacetime login`
- [ ] Cursor installed on all laptops

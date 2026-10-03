# SpacetimeDB

**Prize:** $1,000 / $500 / $200 cash. **Competition:** low (~10 entries at past events).
**Judging:** SpacetimeDB must be the **core** real-time backend: live shared state, multiplayer, instant sync. Past winners were mostly game-like with many screens updating live.

## What we use
- **Tables:** players, floors, devices, plans, actuations, shifts, garden
- **Reducers:** join floor, register device, confirm plan, record actuation, record saved CO₂
- **Scheduled tick** every 10s: grows or wilts each floor's garden
- Python backend writes results to SpacetimeDB over HTTP
- Judges scan a QR code, join, and watch the garden update on every phone

## Setup
```
curl -sSf https://install.spacetimedb.com | sh
spacetime dev --template react-ts
spacetime login
spacetime publish <db> --server maincloud
```
- Free tier is plenty
- Load SpacetimeDB's official Cursor skills first; AI tools default to the old 1.x API

## Watch out
- Reducers can't make network calls or use `Date.now()`/`Math.random()`; use `ctx.timestamp`/`ctx.random()`
- No `async` in procedures; lifecycle hooks must be `export const`
- `u64` = `bigint`, so insert IDs as `0n`; use `ctx.sender` for the caller
- Phones can't reach `localhost`. **Deploy to Maincloud early**
- No SpacetimeDB workshop at MHacks

**Time:** about 6 hours.

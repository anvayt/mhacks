# Final Debate — Full Transcript

Three representatives (main tracks, fun tracks, sponsor tracks) debated the best overall MHacks 2026 combination after reading every file in `main-and-fun-tracks/` and `sponsor-tracks/`. Round 1 was opening statements; in round 2 each saw the others' statements and rebutted or conceded. They reached **consensus in round 2**, so the debate stopped there (max was 4 rounds). Statements below are verbatim. A condensed account is in `../SUMMARY.md`.

## Round 1

### Main-track representative

#### Prompt given (excerpt)
> You are the Main-track representative in a three-way final debate (main vs fun vs sponsor representatives). Read every prior track file, then make an opening case for the best overall MHacks 2026 combination — one main track, which fun track(s), which sponsor tracks — from your side's perspective.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM
- **Core sponsors:** Relay Interactive Agents, Fetch.ai ASI:One, FREE-WILi, SpaceX Make it Legendary
- **Optional sponsors:** ElevenLabs, Figma Best Design, Notability, Capital One Nessie

#### Concessions
- SpaceX stays in the core because the team ranks it first, even though satellite solar data is a weaker 'real space data' fit than Overpass's live orbits. I accept a lower SpaceX win probability (about 12% falling to 6-8%, inference).
- WaterFlow shows SpaceXAI judges rewarded an environmental project built on satellite imagery, but HopHacks' brief had no space-data rule. So that precedent does not settle eligibility at MHacks; only the 4 PM SpaceXAI session can.
- Overpass is not off-theme. Adaptation projects have won sustainability prizes elsewhere (SkySplat, Chilladelphia). My objection is about its relative strength in the main track, not whether it qualifies.
- Relay as the hub is good for the main-track demo, so I accept it as core.
- Fetch.ai stays core because it pays the most sponsor cash and fits an energy agent natively, provided one teammate owns it from hour one and it is cut if ASI:One isn't working end to end with a real action by 6 PM.
- If FREE-WILi fails its 2 PM smoke test, the physical moment is lost, my main-track gain over Overpass shrinks, and I would reopen the choice of design.
- Judged by an LLM is the right fun entry. It costs about 1-2 hours of write-up that the main judges and Fetch need anyway.
- ElevenLabs and Figma are fine optional additions. Figma in particular raises the main-track Usability score.

#### Remaining objections
- Overpass should not be the core. It was shaped to win SpaceX's keyboard prize (about $70 EV). It has no measured CO2 or kWh number, no physical action, and no live local demo in October. It does worse on the newly verified 'Adherence to Theme' criterion than an energy-action design.
- If SpaceXAI rules at 4 PM that satellite irradiance doesn't count, SpaceX should be dropped. The project should not be redesigned around it.
- Capital One should not appear in the main-track pitch. It is only a swap-in, as a 'Green Fund' that writes savings to Nessie, if FREE-WILi fails at 2 PM, because it adds money framing and about 4 hours on top of an already full stack.
- Useless AI works against the Sustainability theme and the Adherence to Theme criterion. Don't tick it.
- Don't build anything for Dumbest Idea. Tick it only if a genuinely comic feature appears on its own and organizers confirm main-track judges don't see fun-track selections (currently unverified).
- SpacetimeDB and Neon each need to be the core backend. Pursuing either would split the build away from the main-track demo.
- Total sponsor-specific work should stay at or under about 26 hours. Every hour beyond the core comes out of polishing the demo the $2,500 and $5,000 judges see.

#### Statement

#### Main-track opening: build the project to win the $2,500 + $5,000, then add sponsors

*Scope: I read all 20 files. Following the relayed user note, I skipped the second 2020 item and used no 2020-dated material.*

##### 1. Why the main track comes first

- **The prizes.** Each main track pays $2,500 and the Grand Prize is $5,000 ([Devpost](https://mhacks-2026.devpost.com/)). The sponsor judge put the whole recommended sponsor stack at about $490 EV. By its own math, one point of main-track win probability is worth about $25, which is more than several sponsor tracks combined (`sponsor-tracks/13-debate-and-verdict.md` §3). A point of Grand Prize probability is worth about $50 (inference).
- **New fact I checked today.** The MHacks 2026 Devpost lists four judging criteria. One of them is **Adherence to Theme**: "Clear demonstration of how the project addresses and contributes to the theme" ([Devpost](https://mhacks-2026.devpost.com/)). Earlier files only inferred this from 2024–25. It is now a published criterion, and it is the one place where project shape alone changes the main-track score.

##### 2. Main track: Sustainability (I agree with the verdict)

- **Smallest verified pool.** The same track text drew 15 of 122 projects in 2025 ([Greenprint filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481)).
- **AI** is the crowd: 47% of 2025 projects listed an LLM (`07-debate-and-verdict.md` §1).
- **FinTech** is likely second-most crowded (15–25%, inference), it drops SpaceX, and it is where budgeting clones pile up (§4 of the same file).
- **Hardware** needs an electronics owner committed before noon. It also loses the Wattson asymmetry: a FREE-WILi stands out in the Sustainability pool but is the minimum in the Hardware pool.

##### 3. My objection: Overpass was shaped to win SpaceX, not Sustainability

The sponsor verdict changed the project from the main/fun verdict's energy-action design to "Overpass," a satellite wildfire watcher. It picked Overpass to make SpaceX's "space data" unambiguous, and SpaceX's prize is keyboards worth about $70 EV. The sponsor judge itself conceded: "Adaptation reads weaker than mitigation" (§4.1). Here is how the two designs compare on what wins this track:

| What the Sustainability judges reward | Overpass | Energy-action design ("Clean Hours") |
|---|---|---|
| Track text: "rethink energy, climate, and resource systems" ([Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)) | Climate alerts (adaptation) | Changes how energy is used (mitigation) |
| One measured impact number (Sustainability advocate's lever #3) | None | kg CO₂ shifted at the live MISO grid intensity |
| Closes the loop | Alert, email, calendar entry | A device on the table switches off |
| Something physical. Hardware took the 2025 Grand, Greenprint and Portal prizes ([Wattson](https://devpost.com/software/wattson-5btsyd)) | No | Yes, a FREE-WILi with an IR transmitter |
| Live local demo | No live Michigan fires in October (Fetch advocate, inference), so the demo uses Yosemite or a replay | The live Midwest grid, right now ([Electricity Maps MISO](https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO)) |
| Event theme: "Digital Garden" ([mhacks.org](https://www.mhacks.org/)) | Not used | A garden that grows with each kWh shifted |

Overpass is not off-theme. Adaptation projects have won sustainability prizes elsewhere, for example [SkySplat](https://devpost.com/software/skysplat) and [Chilladelphia](https://devpost.com/software/chilladelphia). My claim is narrower: it is the weaker main-track entry, and the main track is the larger prize.

##### 4. The project: "Clean Hours"

This combines the Sustainability advocate's "Gridlock," the Fetch advocate's Sketch A and the FREE-WILi advocate's "Off Switch."

- **Data.** Live MISO carbon intensity, plus NASA POWER's satellite-derived solar irradiance. NASA POWER's sources include the CERES satellites ([sources](https://power.larc.nasa.gov/docs/methodology/data/sources/)), and the Photon advocate tested the API live.
- **Brain.** One shared tool layer: `grid_now`, `solar_outlook`, `plan_loads`, `actuate`, `impact`.
- **Hands.** The FREE-WILi learns the IR codes from existing remotes and switches a fan or LED strip on the table ([IR example](https://github.com/freewili/freewili-python/blob/master/examples/send_ir.py)). Its screen shows the garden growing.
- **Three ways to use it, all calling the same brain:**
  - **Relay.** You text it. When the clean window opens, the agent **calls you**: "Cleanest hour is now. Start the dryer?" ([call-a-person](https://docs.relayapp.im/calls/call-a-person.md)).
  - **ASI:One.** "Dry my laundry when the grid is cleanest." A Review card confirms, then the device acts. This matches Fetch's "intent to action" brief and its 20% "Real-World Impact" weight ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
  - **A web dashboard** designed in Figma.
- **The 3-minute pitch.** The judge's phone rings, the fan goes off, and the screen reads "0.4 kWh shifted, X g CO₂." The SpaceX, Fetch and Relay requirements sit inside that same demo.
- **Judged by an LLM.** A backtest: a simulated week of load-shifting against a naive baseline, with kg CO₂ saved.

##### 5. Sponsors

**Core (≈21 sponsor-specific hours):**
- **Relay (≈4 h).** The team named it, and the agent-initiated call is the best software demo moment for any judge. Its workshop build already includes Grok Imagine and ElevenLabs ([README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md)).
- **Fetch.ai (≈7 h).** It has the most cash ($1,250 / $750 / $500), and a physical action fits Fetch better than Overpass's email does. Give it one owner from hour one.
- **FREE-WILi (≈5 h).** This is the main-track differentiator. Its pool was 5 entrants with 2 winners in 2025 ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539)). It is a finished handheld driven by Python over USB, with no soldering. The sponsor verdict left it out because it "doesn't fit this spine." In an energy design it fits natively.
- **SpaceX (≈5 h, mostly work on the product itself).** It is the team's top preference. It needs Cursor and Grok Imagine (the garden renders and the agent's face), with satellite irradiance as the space data. **I concede the space-data fit is weaker than in Overpass.** SpaceXAI did reward an environmental project built on satellite imagery, [WaterFlow](https://devpost.com/software/waterflow-41mrqd), but HopHacks' brief had no space-data rule ([HopHacks](https://hophacks-fall-2026.devpost.com/)), so that precedent proves less than it seems. Optional hedge (≈1–2 h): show which spacecraft measured the data and when it passes next ([CelesTrak weather group](https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json)). If SpaceXAI says no at the 4 PM session ([schedule](https://www.mhacks.org/live)), **drop SpaceX. Don't redesign the project to keep it.**

**Optional:** ElevenLabs (≈1 h, already on the Relay path), Figma (≈3.5 h; it also raises the Usability score), and Notability (only with a free Pro code). **Capital One:** use it only as a swap-in if FREE-WILi fails its 2 PM go/no-go, as a "Green Fund" that writes savings to Nessie and never appears in the main pitch.

**Not entered:**
- SpacetimeDB: needs a multi-user core.
- Neon: "fullest use" isn't worth it here, and it conflicts with SpacetimeDB.
- Photon: the fallback if Relay calls fail.
- FinchNode: it pulls the pitch into health.

##### 6. Fun tracks: Judged by an LLM only

It rewards the same rubric as the main panel, and its write-up doubles as the Fetch README. **Useless AI** works against Adherence to Theme. **Dumbest Idea:** don't build anything for it.

##### 7. Ledger (inference)

| Change from Overpass | Effect |
|---|---|
| Main-track win probability | +3 to +5 points ≈ **+$75–125**, plus Grand Prize upside |
| SpaceX | ≈12% → ≈6–8% chance ≈ **−$25–40** |
| Fetch | Neutral to positive |
| FREE-WILi | Adds a sponsor the verdict valued at **$120–320 standalone** |

Net: positive, and the gain falls in the largest prize pool.

##### 8. Go/no-go checkpoints

- **Noon:** confirm a teammate has iOS 26 and that a FREE-WILi can be borrowed.
- **2 PM:** FREE-WILi smoke test passes, or switch to a simulated device plus Capital One.
- **4 PM:** SpaceXAI ruling on the space data, and Relay calls must work (otherwise switch to Photon).
- **6 PM:** ASI:One completes the flow end to end with one real action, or Fetch is cut.
- **Midnight:** the core works end to end.
- **6 AM:** freeze the UI.


### Fun-track representative

#### Prompt given (excerpt)
> You are the Fun-track representative in a three-way final debate (main vs fun vs sponsor representatives). Read every prior track file, then make an opening case for the best overall MHacks 2026 combination — one main track, which fun track(s), which sponsor tracks — from your side's perspective.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM, Dumbest Idea
- **Core sponsors:** Relay Interactive Agents, SpaceX Make it Legendary, Fetch.ai ASI:One, ElevenLabs
- **Optional sponsors:** Figma Best Design, Capital One Nessie, Notability

#### Concessions
- Fun-track prizes are worth about $0 in dollars ('A useless prize', a Bop It, an LLM-chosen prize; https://mhacks-2026.devpost.com/). The main track and sponsors should never be chosen around them.
- Sustainability stays the main track. Hardware with all three fun tracks is better only if someone commits to owning the electronics by noon.
- Useless AI is not entered by default. It clashes with a 'real problem' Sustainability pitch, and its own advocate conceded this.
- A serious project with one comic feature has low odds of winning Dumbest Idea (about 3–5%, inference). The case for it is spillover, not the Bop It.
- Judged by an LLM has no stage moment, and its model, inputs and rubric are unpublished.
- The comic layer must stay off the ASI:One/Fetch.ai workflow, because Fetch gives 20% of its score to Real-World Impact. The joke targets satellites and pixels, never fires or victims.
- I accept the sponsor verdict's core of Relay + SpaceX + Fetch.ai, the Overpass project, Relay's 4 PM go/no-go with Photon as fallback, and Capital One only as a conditional parametric-payout bolt-on.

#### Remaining objections
- The main/fun verdict says to add Dumbest Idea 'only if a genuine comic hook ships.' That is too passive, because an unplanned joke won't get built at 4 AM. Plan a scoped 1–1.5 h feature at noon (the 'Wave at NOAA-21' satellite selfie) with a midnight go/no-go: if the core isn't working end to end, cut the joke and untick the box.
- ElevenLabs belongs in the core stack, not the bolt-on list. It is the voice on every Relay call and carries the persona, and its published rubric (emotional inflection, personality) is where the comic delivery earns 'best use'. It costs about 1 hour on the workshop path.
- The verdict's worry that ticking Useless AI sends the wrong signal is unverified. Ask on Discord in hour one whether judges can see prize selections, instead of assuming they can. If they can't, ticking Useless AI is a free lottery ticket.
- Judged by an LLM should drive the Devpost structure from hour one: headers matching the four 2026 Devpost criteria (Innovation, Technical Complexity, Usability, Adherence to Theme), plus What we measured and Limitations. It shouldn't be a last-hour write-up. The README/video owner for Fetch.ai should own it.
- Keep real integrations at four or fewer core (Relay, SpaceX/Grok, Fetch.ai, ElevenLabs) so each can be explained in one line to the LLM judge and the 3-minute pitch stays coherent. Add Capital One and Figma only if time allows.

#### Statement

##### Fun-track opening statement (round 1)

**My combination:** Sustainability main · **Judged by an LLM + Dumbest Idea** · core sponsors Relay + SpaceX + Fetch.ai + ElevenLabs · optional Figma, Capital One (parametric payout), and Notability (only with a free code). The project stays as **"Overpass"**, the satellite wildfire agent that both verdicts landed on. I'm not asking to change it. I'm asking the team to plan about 2.5 person-hours for the fun tracks up front instead of hoping they work out.

*Scope: per the relayed user note, I skipped the second 2020 item and used no 2020-dated material.*

###### 1. What fun tracks are worth
- **The prizes are jokes.** On the MHacks 2026 Devpost today: Useless AI pays "A useless prize," Dumbest Idea pays a Bop It, and Judged by an LLM says "Might as well let the LLM decide the prize too!" ([Devpost](https://mhacks-2026.devpost.com/)). Their cash value is about $0.
- **Entering is free and stacks with everything else.** The 2026 rules say you "may enter as many eligible sponsor tracks or prizes as you would like" ([rules](https://mhacks-2026.devpost.com/rules)), and the side quests appear in the Devpost prize list.
- **So the only real argument is spillover.** One percentage point of win probability is worth about $25 on a $2,500 main track and about $50 on the $5,000 Grand Prize (my arithmetic from [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). Fun-track work is only worth doing if it raises those odds or the sponsor odds.

###### 2. Judged by an LLM: enter it and use it as the spec for the write-up
- **Match the published criteria.** Devpost's 2026 criteria are Innovation, Technical Complexity, Usability and Adherence to Theme ([rules](https://mhacks-2026.devpost.com/rules)). The handbook adds "presentation quality" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). Use those four as the Devpost headers, then add "What we measured" and "Limitations."
- **Almost no new work.** The eval table is already in the sponsor plan: grounded vs. ungrounded answers, and predicted pass times vs. real FIRMS timestamps. Fetch.ai already requires a public README listing agent names and addresses, plus a 3–5 minute video ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). The LLM judge almost certainly reads one of those (inference; the model and its inputs aren't published). Cost is about 1–2 person-hours, owned by whoever writes the Fetch README.
- **First hour:** ask on Discord what the LLM reads. Put no hidden instructions to the judge in any text. Organizers can disqualify teams at their discretion (Handbook).

###### 3. Dumbest Idea: plan the joke on purpose, using parts already in the stack
The verdict says to add Dumbest Idea "only if a genuine comic hook ships." A joke nobody planned won't get built at 4 AM. Here is one, scoped to about 1–1.5 hours.

**"Wave at NOAA-21."** Users opt in. A minute before a FIRMS satellite passes overhead, the agent calls them in Relay (agents can place calls; see the [docs](https://docs.relayapp.im/calls/call-a-person.md)): "NOAA-21 is overhead in 60 seconds. Go outside and wave." It then texts a Grok Imagine "satellite selfie" of the user waving, stamped **AI ILLUSTRATION**. Next to it is what the satellite's VIIRS instrument actually recorded: one gray pixel. "Each VIIRS active fire/thermal hotspot location represents the center of a 375m pixel" ([Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms)). The punchline: "You're about four-millionths of a pixel. If your backyard were on fire, though, I'd see that." (My arithmetic: about 0.5 m² ÷ 140,625 m².)

**Why this joke:**
- **It explains the product.** It teaches judges what the instrument can and can't see. That is the Limitations section the LLM judge wants. It's also the honest data sourcing that won SpaceXAI before ([NOVA](https://devpost.com/software/nova-hzgjy0)), and it fits SpaceXAI's "Beauty" criterion: the demo should "feel considered, not assembled" ([Grokathon](https://spacexai-grokathon.devpost.com/)).
- **It turns a known risk into the demo.** The SpaceX advocate warned that generated images shown next to real data hurt trust. Here the fake photo is the joke, shown beside the real pixel.
- **It reuses work already budgeted:** the `next_look` pass predictor (CelesTrak + SGP4), the Relay call, the Grok Imagine postcard and the ElevenLabs voice. The only new pieces are a trigger, a script and a two-panel card.
- **It helps the sponsors that score personality.**
  - Relay's MHacks workshop builds a character with a face and a voice ([README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md)).
  - ElevenLabs' published rubric scores "emotional inflection" and prompt engineering for the agent's personality ([Hack the 6ix](https://hackthe6ix2026.devpost.com/)).
  - SpaceX's brief asks for something "legendary."
- **MHacks has rewarded this pattern.** The 2025 Grand Award went to an absurd premise built on real engineering ([ASI](https://devpost.com/software/artificial-sandwich-intelligence)), and the 2025 fun prize went to a voiced Gemini + ElevenLabs companion ([Judy AI](https://devpost.com/software/judy-ai-4vc9ah)).

**Guardrails so it can't hurt the main entry:**
1. **Joke about the satellite and the pixel only.** Never joke about fires, evacuations or victims. The handbook bans "hateful or toxic" messages.
2. **Order the pitch for the audience.** For Sustainability judges: climate and resource framing in the first 20 seconds, then the live fire call, then the engineering, then the wave as a 15-second closer. For Relay, ElevenLabs and SpaceX judges, open with the wave. Projects "may be judged more than once by different judges" (Handbook), so adjust the pitch each time.
3. **Keep the joke off ASI:One.** Fetch.ai gives 20% of its score to Real-World Impact ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). The ASI:One flow stays the serious "set up a watch" workflow.
4. **Go/no-go at midnight.** If the core product doesn't work end to end by then, cut the joke and untick Dumbest Idea. Ticking the box without a comic feature adds nothing.
5. **Check for a real pass during judging.** Whether a satellite passes over Ann Arbor between 12:30 and 2:30 PM Sunday is unverified. Run `next_pass` at noon. If no pass falls in that window, use a clearly labeled replay mode.

**Honest odds:** a committed comedy build should beat a serious project that has one funny feature. I put our chance of winning Dumbest Idea at about 3–5% (inference). The real bet is spillover. If 90 minutes of work adds one point to the main-track and Grand Prize odds, plus a few points to Relay and ElevenLabs, it pays better per hour than most bolt-on sponsor tracks (inference).

###### 4. Useless AI: skip it unless organizers say otherwise
Its own advocate conceded that it clashes with a "real problem" pitch. The verdict flagged a small risk: a "pointless" checkbox next to a Sustainability pitch could send the wrong signal. Whether judges can see which prizes a team selected is unverified, so ask on Discord. If organizers confirm judges can't see selections, tick it for the satellite selfie as a free lottery ticket. Otherwise, skip it.

###### 5. Full combination and what would change it
- **Main:** Sustainability. **Fun:** Judged by an LLM + Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, and ElevenLabs. I'd move ElevenLabs up from the optional list because it is the voice on every call and carries the comic delivery. On the Relay workshop path it costs about 1 hour.
- **Optional:** Figma; Capital One's parametric payout (only if the core works by midnight); Notability (free code only).
- **Not entered, per the sponsor verdict:**
  - SpacetimeDB: needs a multi-user core.
  - Neon: its "fullest use" bar requires branching, which this product doesn't need.
  - FREE-WILi: no hardware owner yet.
  - Photon: kept as the fallback messaging app if Relay fails.
  - FinchNode: wrong domain.
- **What would change the plan:**
  - **Someone commits to owning the electronics by noon:** switch to the Hardware track with "Skyward" (a desk pointer that tracks satellites) and enter all three fun tracks. A useless machine is a natural Useless AI entry (verdict §8).
  - **Relay calls fail by 4 PM:** move to Photon. The wave gag then runs as an iMessage voice note.


### Sponsor-track representative

#### Prompt given (excerpt)
> You are the Sponsor-track representative in a three-way final debate (main vs fun vs sponsor representatives). Read every prior track file, then make an opening case for the best overall MHacks 2026 combination — one main track, which fun track(s), which sponsor tracks — from your side's perspective.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM
- **Core sponsors:** Relay Interactive Agents, SpaceX Make it Legendary, Fetch.ai ASI:One
- **Optional sponsors:** ElevenLabs, Figma Best Design, Capital One Nessie, Notability

#### Concessions
- Sponsor prizes are small next to the main-track ($2,500) and Grand Prize ($5,000) money. Sponsor hours are justified only where they also improve the main demo.
- SpaceX's prize is weak (keyboards, ≈$70 expected value). It is kept for the domain and the demo, not the payout.
- Relay calls are still unverified on the public build: App Store v1.1 lists no calls, and a 2026-10-02 changelog entry refuses calls to apps that can't take them. Photon must be ready as the fallback surface by 4 PM.
- Capital One does not fit a satellite-fire project natively. It drops from 'build around it' to a conditional parametric-payout bolt-on, built only if the core works end to end by midnight.
- A wildfire agent reads as climate adaptation, which is weaker against the Sustainability text than an energy project. The emissions-accounting fix helps but does not fully close that gap.
- Fetch.ai costs about 7 hours and needs a second submission that every teammate must join. ASI:One is a text chat that main-track judges may never see.
- Notability is not free: Pro costs $79.99 with no individual trial, so enter only with an expo code or an existing account.
- SpacetimeDB and FREE-WILi have better cash-per-competitor or odds than SpaceX, but they don't fit this project coherently. Choosing SpaceX over them is a preference-driven trade, worth about the same in expected value.
- All expected-value figures are inferences resting on small samples (2 SpaceX twin events, no Relay precedent, n=15 for Fetch.ai at MHacks 2025).

#### Remaining objections
- Against an energy-domain main pitch (Clean Hours or Gridlock built on NASA POWER): satellite-derived irradiance is weak 'space data' for SpaceX judges, so it would likely cost the team's top sponsor. Don't make that switch unless SpaceXAI rejects Earth-observation plus orbit data at 4 PM.
- Against building for Dumbest Idea or Useless AI: a joke premise conflicts with Fetch.ai's 20% Real-World Impact weight and its 'avoid simple chatbots' rule, and with Capital One's 'improve financial lives' brief. Enter Dumbest Idea only if a genuine comic feature ships unprompted.
- Against a Hardware flip without a confirmed electronics owner: FREE-WILi's 1 PM workshop clashes with Relay's, loaners are unconfirmed, and the main-track result would rest on unknown skills.
- Against FinTech main: the cash-max stack (SpacetimeDB + Fetch.ai + Capital One, ≈$500) earns about what the preference-aligned stack earns (≈$490–565) and gives up SpaceX.
- Against entering both Relay and Photon, or both Neon and SpacetimeDB: a 3-minute pitch can sell only one messaging surface and one backend. Doubling up is the kind of token use sponsor judges see through.
- Still unverified: whether SpaceXAI accepts FIRMS plus orbit data as 'space data', whether Relay calls work on today's build, and whether Fetch.ai judges reward a climate entry (only 1 of 48 past Fetch winners was green).

#### Statement

##### Sponsor-track opening: one agent, three ways to reach it, built on Sustainability

**Proposed combination**
- **Main track:** Sustainability.
- **Fun track:** Judged by an LLM.
- **Core sponsors:** Relay, SpaceX "Make it Legendary", and Fetch.ai ASI:One.
- **Bolt-ons, in priority order:** ElevenLabs, then Figma, then Capital One (only if the core works end to end by midnight), then Notability (only with a free Pro code).

I'm keeping both verdicts' picks. My job here is to show that the sponsor stack fits them, not to fight them. Per the relayed user note, I skipped the second 2020 item and cite no 2020 material.

###### 1. Sponsor money is real, but the main track is worth more
- **The big prizes:**
  - A main-track win pays $2,500 and the Grand Prize pays $5,000 ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
  - One extra point of main-track probability is worth about $25 [inference].
  - So sponsor hours have to make the main demo better too, not just tick a box.
- **Three tracks do both: Relay, SpaceX and Fetch.ai.**
  - Fetch.ai pays $1,250 / $750 / $500 in cash. I re-checked this on Devpost today, along with SpacetimeDB's $1,000 / $500 / $200 cash and the separate [MLH] Best Use of ElevenLabs prize (wireless earbuds) ([Devpost](https://mhacks-2026.devpost.com/)).
  - At MHacks 2025, 15 of 122 projects opted into Fetch.ai's prizes and 3 of them won ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535)). Its hard requirements thin the field.
- **Expected value, using the sponsor verdict's discounted figures [inference]:**

| Track | Expected value |
|---|---|
| Fetch.ai | ≈ $180 |
| Relay | ≈ $175 |
| SpaceX | ≈ $70 |
| ElevenLabs | ≈ $40 |
| Figma | ≈ $23 |
| **Core + ElevenLabs + Figma** | **≈ $490** |
| With the Capital One payout feature | ≈ $565 |

- **The cash-max alternative pays no better.** SpacetimeDB + Fetch.ai + Capital One earns about $500, and it forces a multiplayer, finance-leaning product ([sponsor verdict](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md)). The team doesn't have to give up its preferences to earn the same money.

###### 2. The project: "Overpass," with every sponsor doing real work
**The data.** Overpass takes NASA FIRMS fire detections from each satellite and propagates those same satellites' orbits from CelesTrak with SGP4. I pulled today's keyless NOAA-20 file: about 1,800 detections in 24 h, with `satellite` and `frp` (fire radiative power) columns ([FIRMS CSV](https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv)).

**The test for each sponsor:** would that sponsor's judge see real use, or a box being ticked?
- **SpaceX (native).**
  - The rule is "Real space data goes in," built with Cursor, plus Grok Imagine or the Voice API ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Orbit propagation makes the "space data" claim unambiguous.
  - Precedent: WaterFlow, an environmental satellite project with Grok as a careful, no-invented-data explainer, won SpaceXAI at HopHacks Fall 2026 ([WaterFlow](https://devpost.com/software/waterflow-41mrqd)).
- **Relay (native; it's the hub).**
  - Relay's own MHacks workshop uses `grok-imagine-image-2.0`, `grok-imagine-video-1.5-lite` and ElevenLabs `eleven_v4_turbo`. Its last step is "Your agent calls you" ([README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md)).
  - So one build covers Relay, SpaceX's tooling rule and ElevenLabs.
  - The demo moment: the agent calls the judge's phone when a new detection lands.
- **Fetch.ai (a second way into the same agent).**
  - The same tools sit behind a uAgent. In ASI:One a user sets up a watch, confirms a Review card, and the agent sends an alert or edits a calendar.
  - That matches the hackpack's requirements for "meaningful tool execution" and completing the workflow "entirely within an ASI:One conversation" ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
- **ElevenLabs.** It is the call voice, so the work is about 1 h of polish.
- **Figma.** The live globe is real UI: it's the web view main-track judges see and the agent's video "camera."
- **Fit with Judged by an LLM.** Fetch.ai already requires a public repo, a README with agent addresses and a demo video. An eval table (grounded vs. ungrounded answers; predicted next satellite pass vs. actual FIRMS timestamps) gives the LLM judge numbers it can score.

###### 3. Answering the Sustainability objection before the main-track rep raises it
The track text says "rethink energy, climate, and resource systems" ([MHacks 26 Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). A fire alert agent reads as adaptation, which is a weaker fit.

**My fix: carbon accounting from space.**
- **Burned biomass.** FIRMS reports fire radiative power. A standard coefficient, 0.368 kg of biomass burned per MJ of fire radiative energy (Wooster et al. 2005), converts that to biomass burned. Satellite emissions inventories use it ([Li et al. 2018](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017JG004279); [Kaiser et al. 2012](https://bg.copernicus.org/articles/9/527/2012/bg-9-527-2012.pdf)).
- **CO₂.** Published emission factors by fire type then convert biomass burned into CO₂ ([Andreae 2019](https://acp.copernicus.org/articles/19/8523/2019/)).
- **The pitch line:** "This fire has released roughly X t of CO₂, and NOAA-21 looks again in 47 minutes."
- **Caveat [inference]:** satellites in polar orbit only see a fire once in a while, so the estimate is order-of-magnitude. Label it as an estimate and put it in the Limitations section, where it also helps with the LLM judge.
- **Cost:** about 2 h. It moves the pitch from "alert app" to climate-system measurement.

###### 4. The team's lean, assessed honestly
- **SpaceX: keep it.** Keep it for the domain and the demo, not the keyboards (≈ $70 expected value).
- **Relay: keep it, with a go/no-go at 4 PM.** I re-checked today:
  - The App Store build is still v1.1 (Sep 20). It lists groups, voice notes and attachments but not calls, and it requires iOS 26 ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)).
  - Relay's changelog added a `422` error on 2026-10-02 for calling "a person whose app cannot take calls" ([changelog](https://docs.relayapp.im/changelog.md)).
  - Settle it at the 1 PM workshop. If calls don't work on a teammate's phone by 4 PM, switch the messaging surface to Photon. Its twin-event winner used Grok ([News Next Door](https://devpost.com/software/news-next-door)), and the tools layer doesn't change.
- **Capital One: demote it to a conditional bolt-on.**
  - The prize is $300 / $75 / $25 per member ([Devpost](https://mhacks-2026.devpost.com/)), but satellite fire data doesn't fit it natively.
  - The one version that does real work is a **parametric payout**: a detection within X km of an insured address triggers a Nessie deposit, the app reads the balance back, and Relay calls the user. A balance widget alone would fail the box-ticking test.
  - Build it only if the core runs end to end by midnight.

###### 5. Tracks I'm not stacking, and why
- **SpacetimeDB.** Best cash per competitor, but it must be the core of a *multi-user* product ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Relay chats are one person each, so adding it here would be forced.
- **FREE-WILi.** The least-contested prize: 5 entrants and 2 winners in 2025 ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539)). But it needs someone to own the hardware, it fits an energy project better than this one, and its workshop is at the same hour as Relay's.
- **Neon.** The prize is credits, and "fullest use" would mean using database branching, which this project doesn't need. It also conflicts with SpacetimeDB.
- **Photon.** It's a fallback surface only. Pitching both Relay and Photon splits the story.
- **FinchNode.** Adding it turns the pitch toward health.
- **Notability.** Pro costs $79.99, with no individual free trial ([pricing](https://notability.com/pricing)). Enter only with a free code.

###### 6. Fun tracks from the sponsor side
- **Judged by an LLM costs nothing.** Its write-up is the same material Fetch.ai already requires.
- **Dumbest Idea and Useless AI conflict with my cash track.** Fetch.ai scores "Real-World Impact & Usefulness" at 20% ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). A joke premise would dilute both Fetch.ai and the Sustainability pitch.

###### 7. Hours, owners and checkpoints
- **Hours:** about 16 sponsor-specific person-hours for the core, about 20 with ElevenLabs and Figma, and about 26 at the most.
- **Owners:**
  - P1: Relay. Needs an iOS 26 phone.
  - P2: SpaceX and the data.
  - P3: Fetch.ai, owning it from the first hour.
  - P4: design and the pitch.
- **Checkpoints:**
  - **1 PM:** Relay workshop.
  - **2 PM:** Fetch.ai workshop.
  - **4 PM:** SpaceXAI session. Ask whether Earth-observation plus orbit data counts, then decide Relay go/no-go.
  - **About 6 PM:** Fetch.ai go/no-go. ASI:One must work end to end with one real action, or drop it.
  - **Midnight:** decide on Capital One.
- **What would change the plan:**
  - SpaceXAI rejects the data: switch to an energy agent, with Capital One promoted to core.
  - A confirmed electronics owner appears by 2 PM: switch to the Hardware variant with FREE-WILi.


## Round 2

### Main-track representative

#### Prompt given (excerpt)
> You are the Main-track representative, round 2 of the final debate. Read the other representatives' previous statements, rebut or concede, and update your proposed combination; the goal is consensus on main track + fun track(s) + core sponsor tracks.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM, Dumbest Idea
- **Core sponsors:** Relay Interactive Agents, SpaceX Make it Legendary, Fetch.ai ASI:One, ElevenLabs, FREE-WILi
- **Optional sponsors:** Figma Best Design, Capital One Nessie, Notability

#### Concessions
- NASA POWER can't drive a live decision. My probe today returned only fill values (-999) for every hourly reading from Aug 1 to Oct 3 for Ann Arbor, and the daily API's last valid day is Sep 28. My round-1 'space data' was weaker than even the sponsor rep said.
- 'No live local demo' for Overpass was overstated. Today's VIIRS 24-hour files show 27, 22 and 10 detections in a Michigan bounding box (NOAA-20, NOAA-21, Suomi NPP). All are low or nominal confidence, with a maximum of 7.2 MW. The data is live; only the dramatic story is missing.
- ElevenLabs moves into the core. It is the call voice on the Relay workshop path, costs about 1 hour, and doesn't dilute the main demo.
- Dumbest Idea is entered with a planned 1-1.5 hour comic feature, cut at midnight if the core isn't working end to end. The fun rep is right that a joke nobody planned won't get built.
- Innovation may favor Overpass. Carbon-aware scheduling is a more familiar idea (inference), so my main-track edge rests on Adherence to Theme and the physical demo, not on novelty.
- GOES-19 data narrows the SpaceX gap but does not close it. It is still Earth observation, and Overpass's orbit propagation stays the more unambiguous 'real space data'.
- If SpaceXAI says at the Expo that only orbit or mission data counts, or FREE-WILi has no loaners, I accept Overpass as the project and drop FREE-WILi.
- Capital One stays a conditional bolt-on in both branches: the parametric payout under Overpass, the Green Fund under Clean Hours. It is never core and never in the main pitch.

#### Remaining objections
- Overpass's carbon accounting measures CO2 the product can't change. Against Devpost's 'addresses and contributes to the theme' criterion, it doesn't close the gap with a design whose number is CO2 avoided by its own action.
- Don't wait until the 4 PM SpaceXAI session for the space-data ruling. Ask SpaceXAI and FREE-WILi at the 11:30 AM Sponsor Expo, before the design is locked at noon.
- If SpaceXAI's Expo answer is vague rather than a 'no', default to Clean Hours. On a plain reading, GOES-19 radiation measured 17 minutes ago is 'real space data'.
- In the Clean Hours branch, FREE-WILi is core, not a bolt-on. It is the main-track differentiator (the Wattson pattern) and the least-contested sponsor pool.
- Once Clean Hours is chosen, a failed 2 PM FREE-WILi smoke test means simulating the device. It does not mean redesigning mid-hack.
- The comic feature gets 15 seconds or less in the main-track pitch, placed after the impact number, and stays off ASI:One.
- Keep sponsor-specific work at or under about 26 hours. Clean Hours core plus Figma comes to about 25.5.
- Useless AI stays unticked unless organizers confirm that main-track judges can't see fun-track selections.

#### Statement

#### Main-track round 2: decide the design at the 11:30 Sponsor Expo

*Scope: following the relayed user note, I skipped the second 2020 item. Nothing below is dated 2020.*

##### 1. What we already agree on
All three of us now propose the following:
- **Main track:** Sustainability.
- **Fun track:** Judged by an LLM.
- **Core sponsors:** Relay, SpaceX and Fetch.ai.
- **Fallbacks and gates:** Photon is used only if Relay calls fail by 4 PM. Fetch is cut if ASI:One doesn't work end to end by 6 PM.
- **Excluded:** Capital One never goes in the core. SpacetimeDB, Neon, FinchNode and Useless AI stay out.

I suggest we treat all of that as settled. One question is still open: **Overpass (wildfire detections plus satellite orbits) or Clean Hours (grid-aware load shifting with a physical off switch)?** The FREE-WILi decision, the Capital One variant and the joke all depend on that answer.

##### 2. What I concede, including new evidence against my own round 1
- **NASA POWER can't drive a live decision.** I queried POWER's hourly API for Ann Arbor today. It returned only the −999 fill value for every hour from Aug 1 to Oct 3, and the daily API's last valid day is Sep 28 ([POWER hourly API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)). The sponsor rep was right that this space data was weak. It was weaker than they said, because it was 5 days stale.
- **I overstated "no live local demo."** Today's 24-hour VIIRS files show detections inside a Michigan bounding box: 27 from NOAA-20 ([CSV](https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv)), 22 from NOAA-21 ([CSV](https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv)) and 10 from Suomi NPP. By my count, none is high-confidence and the largest is 7.2 MW of fire radiative power. So Overpass does have live local data. What it lacks is a live local *story*.
- **ElevenLabs moves to core.** The fun rep is right. It is the call voice on the Relay workshop path, it costs about 1 hour, and it dilutes nothing.
- **Dumbest Idea: enter it, with the feature planned and gated.** The fun rep is right that an unplanned joke won't get built at 4 AM. I accept a 1–1.5 hour feature scoped at noon and cut at midnight if the core isn't working end to end. With main-track judges, it stays a closer of 15 seconds or less, after the impact number. That matches the pitch order the fun rep already proposed.
- **Innovation may favor Overpass.** Carbon-aware scheduling is probably a more familiar idea than an orbit-aware fire watcher (inference). My claim to an edge rests on Adherence to Theme and the demo, not on novelty.

##### 3. The SpaceX fix: use GOES-19 instead of NASA POWER
- **The satellite.** GOES-19 has been the operational GOES-East satellite since April 7, 2025, at 75.2°W ([NOAA NESDIS](https://www.nesdis.noaa.gov/news/noaas-goes-19-now-operational-goes-east-providing-critical-new-data-forecasters)).
- **The data.** Its ABI instrument produces a **Downward Shortwave Radiation** product: how much sunlight reaches the ground, measured from orbit. The files sit in NOAA's public S3 bucket and need no key.
  - At 12:29 UTC today, the newest file covered the 12:00 scan and was written at 12:17 ([bucket listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-DSRF/2026/276/); [AWS registry](https://registry.opendata.aws/noaa-goes/)). That is about 17 minutes behind, with a new scan every 10 minutes.
  - Each file is about 26 MB of netCDF. Reading the Ann Arbor pixel should take about 1–2 hours of Python work (inference).
- **A live image panel.** The GOES-19 Great Lakes GeoColor image had been updated 3 minutes before I fetched it ([STAR CDN](https://cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/cgl/GEOCOLOR/latest.jpg)). That gives a "what the satellite sees over Michigan right now" panel.
- **The new pitch line:** "GOES-19 measured the sun over Ann Arbor 17 minutes ago, MISO is at X g/kWh, so your dryer starts now."
- **The limit.** This is still Earth-observation data, the same kind as FIRMS. Overpass keeps one real edge: propagating the satellites' orbits makes its "space data" claim unambiguous. GOES narrows the SpaceX gap but does not close it.

##### 4. Why I still claim the main-track edge
The sponsor rep's carbon accounting is solid work, but it measures CO₂ that **the product cannot change**.
- **The criterion.** The Devpost's Adherence to Theme criterion asks for a "clear demonstration of how the project addresses and contributes to the theme" ([Devpost](https://mhacks-2026.devpost.com/)).
- **The track text.** It asks teams to "rethink energy, climate, and resource systems" ([Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)).
- **Clean Hours.** Its number is CO₂ **avoided by an action the product took**, on a fan the judge watches switch off. That is the pattern of Wattson, which won this exact track text in 2025 ([Wattson](https://devpost.com/software/wattson-5btsyd)).
- **Overpass.** Its number is what a fire emitted while we watched.

Both designs are on-theme, but only Clean Hours changes the emissions it reports. How much judges weigh that is my inference, not a published weighting.

##### 5. Proposal: settle it at 11:30, before the design is locked
The Saturday schedule runs as follows ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)):
- 11:30 AM: Sponsor Expo.
- 12:00 PM: hacking starts.
- 1 PM: FREE-WILi and Relay workshops (same hour).
- 4 PM: SpaceXAI session.

In round 1, all three of us scheduled the SpaceX ruling for 4 PM, four hours after the design would already be locked. Instead, ask both deciding questions at the Expo, at the SpaceXAI and FREE-WILi tables:

| Answer at the 11:30 Expo | Build | Core sponsors |
|---|---|---|
| SpaceXAI says satellite Earth-observation data counts (or states no rule against it), **and** FREE-WILi confirms loaner kits | **Clean Hours** | Relay, SpaceX, Fetch.ai, ElevenLabs, FREE-WILi |
| SpaceXAI says only orbit or mission data counts | **Overpass**, which keeps the team's top sponsor | Relay, SpaceX, Fetch.ai, ElevenLabs |
| No FREE-WILi loaners | **Overpass**. Without the physical moment, my main-track gain falls below the SpaceX cost | Same as above |
| Clean Hours chosen, then the 2 PM FREE-WILi smoke test fails | Stay on Clean Hours with a simulated device. Capital One's "Green Fund" (savings written to Nessie) becomes the bolt-on | Relay, SpaceX, Fetch.ai, ElevenLabs |

Every branch keeps SpaceX and Relay. Capital One stays a conditional bolt-on: the parametric payout under Overpass, the Green Fund under Clean Hours.

##### 6. Ledger: Clean Hours compared with Overpass (all inference)
| Item | Change |
|---|---|
| Main track | +3 to +5 points ≈ +$75–125, plus Grand Prize upside from a physical demo |
| FREE-WILi | +$120–320 (the sponsor verdict's standalone range) |
| SpaceX | About −$15–30 with GOES data. My round-1 estimate was −$25–40, based on stale data |
| **Net** | **About +$180–400 if both gates pass.** Roughly break-even if FREE-WILi fails after we commit, which is why the loaner question comes first |

##### 7. Fun tracks
**Enter Judged by an LLM and Dumbest Idea.** The joke depends on the branch:
- **Overpass:** the fun rep's "Wave at NOAA-21."
- **Clean Hours: "The 3 AM call."** At the cleanest hour of the night, the agent phones you, overly earnest: "Wind's up across MISO. This is your dryer's moment." If you decline, the garden on the FREE-WILi screen wilts. It reuses the Relay call and the ElevenLabs voice.

Both jokes stay off ASI:One, because Fetch.ai gives 20% of its score to Real-World Impact. Skip Useless AI unless organizers confirm that main-track judges can't see fun-track selections.

##### 8. Hours
- **Clean Hours core:** about 22 sponsor-specific hours (Relay 4, SpaceX 5, Fetch 7, ElevenLabs 1, FREE-WILi 5).
- **With Figma:** about 25.5 hours, under my 26-hour cap.
- **Staffing:** Relay and FREE-WILi hold their workshops at the same hour (1 PM), so P1 goes to Relay and P4 to FREE-WILi.


### Fun-track representative

#### Prompt given (excerpt)
> You are the Fun-track representative, round 2 of the final debate. Read the other representatives' previous statements, rebut or concede, and update your proposed combination; the goal is consensus on main track + fun track(s) + core sponsor tracks.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM, Dumbest Idea
- **Core sponsors:** Relay Interactive Agents, Fetch.ai ASI:One, FREE-WILi, SpaceX Make it Legendary, ElevenLabs
- **Optional sponsors:** Figma Best Design, Capital One Nessie, Notability

#### Concessions
- I switch from Overpass to the main rep's Clean Hours. Adherence to Theme is now a verified Devpost criterion, and Wattson ('Nurture a pet by being sustainable') won Greenprint plus FREE-WiLi with a playful loop, so the energy-action design is the stronger host for both fun tracks.
- Useless AI: skip it entirely. Devpost prize filters show opt-ins publicly, so a 'pointless' tick is not invisible, and with Adherence to Theme confirmed, the roughly 1% odds don't justify the signal risk.
- My round-1 'Wave at NOAA-21' gag is retired unless the team picks Overpass.
- Dumbest Idea odds stay low (about 3-5%, inference). The case is spillover to presentation, Relay and ElevenLabs, not the Bop It.
- The comic persona stays off ASI:One. Fetch.ai gives Real-World Impact 20%, and the Review-card flow stays serious.
- Clean Hours lowers the odds on SpaceX, the team's top-preference sponsor. That trade is real, and I accept it for the main-track gain.
- FREE-WILi joins the core per the main rep. That exceeds my round-1 cap of 4 integrations, which I accept by counting Relay plus ElevenLabs as one voice path.
- Figma is optional, only if the core is ahead of schedule and total sponsor work stays under about 26 h.
- If FREE-WILi fails its 2 PM go/no-go, Fern's 'I asked nicely' moment runs against a simulated device and is weaker. Capital One's Green Fund then swaps in per the main rep.

#### Remaining objections
- Dumbest Idea should not depend on a comic feature appearing on its own. Budget 1-1.5 h for the Fern escalation ladder (text, then call, then IR off) at noon, with a midnight cut line. It reuses the core's Relay call, IR action and garden, so it adds no new integration.
- ElevenLabs belongs in the core, not the bolt-on list. It is Fern's voice on every Relay call, and one integration now competes for two prizes: the ElevenLabs sponsor track and the MLH Best Use of ElevenLabs, verified on Devpost today. It costs about 1 h.
- Replace the CelesTrak hedge with the live GOES-19 Upper Mississippi Valley GeoColor 'window' (keyless, returned 200 today). Judges see real satellite imagery of the clouds over the grid's region. It costs about 1 h, narrows SpaceX's space-data gap and adds no net hours.
- The Judged by an LLM structure starts at hour one, not the last hour. Use headers for the four verified Devpost criteria plus 'What we measured' (CO2 backtest and actuation log) and 'Limitations' (average vs marginal intensity). P3, who owns the Fetch README, owns it.
- If the team overrides and picks Overpass, the round-1 plan applies: the wave gag as the Dumbest Idea feature, with the same midnight cut line.

#### Statement

##### Fun-track rep, round 2: back Clean Hours, and make the joke the garden itself

*Scope: per the relayed user note, I skipped the second 2020 item and cite no 2020 material.*

###### 1. Where I land
I'm moving from Overpass to the main rep's **Clean Hours**. I'm not changing sides on the main track (Sustainability for all three of us). I'm changing because Clean Hours gives both fun tracks I'm entering a stronger footing:

- **Judged by an LLM wants a measured number.** Clean Hours produces one: kg CO₂ shifted against a naive baseline. Overpass's best number was an order-of-magnitude burn estimate that the sponsor rep had to put under Limitations.
- **Dumbest Idea wants a joke people laugh at in the room.** In Clean Hours the joke can *be* the core action rather than a side feature (§3).
- **The criterion is now confirmed.** I re-checked the MHacks 2026 Devpost today. "Adherence to Theme" is a published criterion: "Clear demonstration of how the project addresses and contributes to the theme" ([Devpost](https://mhacks-2026.devpost.com/)). A garden that grows when you shift load fits both the track text ("rethink energy, climate, and resource systems"; [Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)) and the "Digital Garden" event theme ([mhacks.org](https://www.mhacks.org/)).

**Combination:** Sustainability · **Judged by an LLM + Dumbest Idea** · core sponsors Relay, Fetch.ai, FREE-WILi, SpaceX and ElevenLabs · optional Figma, Capital One (only as the FREE-WILi-failure swap-in) and Notability (free code only).

###### 2. Responses to the other two reps

**Main rep. I accept:**
- **The Wattson precedent settles the tone question.** The 2025 Greenprint winner's tagline was "Nurture a pet by being sustainable." It was a playful loop on a FREE-WiLi, and it won both Greenprint and Best Use of FREE-WiLi ([Wattson](https://devpost.com/software/wattson-5btsyd), checked today). A playful hook on a real outcome has already won this exact track at MHacks.
- **The decision has to be made at noon.** The SpaceXAI ruling comes at 4 PM ([schedule](https://www.mhacks.org/live)). The team has to commit to a project before knowing whether satellite irradiance counts. So go with the design that wins the larger prize pool (inference).

**Main rep. I reject:** "Don't build anything for Dumbest Idea; tick it only if a comic feature appears on its own." A joke nobody plans doesn't get written at 4 AM. Also, in Clean Hours the comic layer is how the impact number gets *delivered*, so it doesn't compete with the pitch.

**Sponsor rep. I accept:**
- Clean Hours lowers SpaceX's odds. SpaceX is the team's top preference, and I say that plainly.
- ASI:One stays the serious flow: Fetch gives 20% of its score to Real-World Impact ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).

**Sponsor rep. I offer a cheaper hedge** than the main rep's CelesTrak one: a live **GOES-19 "window"**. NOAA's Upper Mississippi Valley GeoColor image is keyless, and it returned HTTP 200 today ([latest.jpg](https://cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/umv/GEOCOLOR/latest.jpg); [sector page](https://www.star.nesdis.noaa.gov/GOES/sector.php?sat=G19&sector=umv)).
- Judges see real satellite imagery of the clouds over the region the grid draws on. That this sector overlaps much of the MISO footprint is my inference. It sits alongside NASA POWER's satellite-derived irradiance ([sources](https://power.larc.nasa.gov/docs/methodology/data/sources/)).
- It costs about 1 h and replaces the CelesTrak hedge instead of adding to it.
- It doesn't make SpaceX as strong as Overpass. It narrows the gap.

**Sponsor rep. I reject:** "a joke premise conflicts with Fetch." The premise here isn't a joke: shifting load to clean hours is the product. Only the voice on the Relay call is funny.

###### 3. The fun-track plan on Clean Hours

**Judged by an LLM (always enter, about 1 h net, owned by P3, who owns the Fetch README):**
- **Devpost headers from hour one:** the four verified criteria (Innovation, Technical Complexity, Usability, Adherence to Theme), then *What we measured* and *Limitations* ([Devpost](https://mhacks-2026.devpost.com/)).
- **What we measured:**
  - A backtest: a real past week of MISO intensity, our schedule against the naive one, reported as kg CO₂.
  - An **actuation log**: IR commands sent, success rate and latency. An LLM can't see the fan switch off, so the log is how the hardware shows up in text (inference; the verdict rated hardware as Judged by an LLM's weakest pairing).
- **Limitations:** say plainly that the backtest uses average rather than marginal grid intensity (inference: this is the main technical caveat in load-shifting claims).
- **First hour:** ask on Discord what the LLM judge reads. Put no hidden instructions to the judge anywhere. The Handbook allows disqualification at organizers' discretion ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).

**Dumbest Idea: "Fern," a houseplant with a phone line and an IR blaster** (about 1–1.5 h). This builds on the Sustainability advocate's "houseplant that roasts you" (`01-main-sustainability.md`). Fern is the garden's voice in Relay, with an opt-in **"tough love" mode** that escalates in three steps:
1. A text: "Grid's on coal. Hold the dryer."
2. A **call** in an ElevenLabs voice ([call-a-person](https://docs.relayapp.im/calls/call-a-person.md)): "I'm a fern. I will wilt."
3. If you ignore it, Fern fires the learned IR code itself ([IR example](https://github.com/freewili/freewili-python/blob/master/examples/send_ir.py)): "I asked nicely." The fan on the table goes off, and the garden on the device screen perks up.

**Why this joke works:**
- **Almost nothing new to build.** The text, the call, the IR action and the garden are all already in the core. Fern adds a persona prompt, the three-step script, and wilt/bloom states rendered with Grok Imagine (labeled as AI illustration and never used as data). The art also helps meet SpaceX's Imagine requirement.
- **It reinforces Adherence to Theme**, because the joke *is* the garden.
- **It suits the sponsors that score personality.** Judy AI won MHacks 2025's fun prize as a voiced Gemini + ElevenLabs companion ([Judy AI](https://devpost.com/software/judy-ai-4vc9ah)). ElevenLabs now has two prizes here, the sponsor track and an MLH "Best Use of ElevenLabs" ([Devpost](https://mhacks-2026.devpost.com/)), which is why I keep it in the core.

**Guardrails:**
- Roast appliance habits, never people. The Handbook bans "hateful or toxic" messages.
- Tough-love mode is opt-in and acts only on devices the user has registered.
- No persona on ASI:One.
- For the Sustainability pitch: impact number in the first 20 seconds, then the call, then the engineering. Fern gets 15 seconds. For Relay and ElevenLabs judges, open with the call (projects "may be judged more than once"; [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).
- **Midnight cut line:** if the core isn't working end to end, Fern falls back to a neutral voice and Dumbest Idea gets unticked.

**Honest odds:** about 3–5% to win the Bop It (inference). The real case is the spillover to presentation, Relay and ElevenLabs.

**Useless AI: I now concede, so skip it.** Devpost's prize filters show every team's opt-ins to anyone. That's how we counted 2025's entries ([example filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481)). So the "invisible free lottery ticket" I argued for in round 1 doesn't exist. With Adherence to Theme now a confirmed criterion, ticking "gloriously pointless" carries a small but real risk for roughly 1% odds (inference).

**My round-1 "Wave at NOAA-21" gag:** retired, unless the team chooses Overpass. In that case it stands as written.

###### 4. Hours and checkpoints
- **Hours:** about 21 h for the main rep's core, plus about 1 h for ElevenLabs, about 1–1.5 h for Fern and about 1 h net for the LLM write-up. The GOES swap adds nothing. **Total: about 24–24.5 h, under the 26-h cap.** Figma (about 3.5 h) goes in only if the core is ahead of schedule.
- **Noon:** Devpost skeleton written; Discord question about the LLM judge sent; iOS 26 phone and FREE-WILi availability confirmed.
- **2 PM:** FREE-WILi go/no-go. If it fails, Fern's "I asked nicely" plays against a simulated device. That's weaker but still funny, and Capital One's Green Fund swaps in.
- **4 PM:** SpaceXAI ruling and Relay go/no-go.
- **Midnight:** Fern go/no-go.
- **6 AM:** freeze the UI and Fern's script together.

###### 5. What would change my position
- **The team picks Overpass:** same fun-track set, with the wave gag as the joke.
- **An electronics owner commits by noon:** the Hardware variant, with all three fun tracks.


### Sponsor-track representative

#### Prompt given (excerpt)
> You are the Sponsor-track representative, round 2 of the final debate. Read the other representatives' previous statements, rebut or concede, and update your proposed combination; the goal is consensus on main track + fun track(s) + core sponsor tracks.

#### Proposed combination
- **Main:** Sustainability
- **Fun:** Judged by an LLM, Dumbest Idea
- **Core sponsors:** Relay Interactive Agents, Fetch.ai ASI:One, FREE-WILi, SpaceX Make it Legendary, ElevenLabs
- **Optional sponsors:** Figma Best Design, Capital One Nessie, Notability

#### Concessions
- Project shape: I concede Overpass to the energy-action design (Clean Hours). Once FREE-WILi is counted, sponsor EV rises (≈$490 to ≈$585–800, inference) on top of the main-track gain under the published Adherence to Theme criterion.
- FREE-WILi moves from 'not entered' to core. It is native in an energy design: IR off-switch, garden on screen, physical button. Its 2025 pool was 5 entrants with 2 winners.
- If SpaceXAI rules at 4 PM that Earth-observation data doesn't count, drop SpaceX and don't redesign. This reverses my round-1 objection.
- Capital One is only a swap-in if FREE-WILi fails its 2 PM test, and stays out of the main pitch. I accept the main-track rep's rule.
- ElevenLabs moves to core (fun rep is right). Relay's 2026-10-01 @relaymessenger/elevenlabs package makes it the voice and lip-sync of every call for about 1 h.
- Dumbest Idea: I accept a planned, gated comic feature (≤1 h, midnight go/no-go, kept off ASI:One) instead of 'only if it ships unprompted'. It is now a by-product of the Relay/ElevenLabs persona rather than separate work.
- SpaceX's fit is weaker in an energy design than in Overpass even with live GOES data, because there is no orbit-propagation hedge. I put it at about 8–10%, down from about 12%.

#### Remaining objections
- NASA POWER must not be SpaceX's space data. I checked today: its daily series for Ann Arbor ends Sept 28 and the hourly series has no valid value since Aug 1, so it cannot drive a live decision and reads as decoration. Use GOES-19 instead: Downward Shortwave Radiation hourly (today's 12:00 UTC file posted 12:17 UTC) plus the 5-minute clear-sky mask, both on the public noaa-goes19 S3 bucket.
- The fun rep's 'Wave at NOAA-21' joke doesn't carry over to Clean Hours. Replace it with a melodramatic Digital Garden houseplant persona: a Rive character in the call, voiced by ElevenLabs. Tick Dumbest Idea only if it ships by midnight, and ask on Discord whether main judges see fun-track selections.
- Clean Hours' edge over Overpass depends on FREE-WILi working by 2 PM and Relay calls working by 4 PM. If both fail, most of the edge is lost. The team should keep the design anyway but understand the advantage is conditional.
- Still unverified: FREE-WILi loaner availability and which firmware/library it runs; Electricity Maps (or another grid-carbon API) access for MISO; whether SpaceXAI accepts GOES Earth-observation data; whether Relay calls work on today's App Store build; whether the GOES NetCDF parse fits in about 2–3 h.
- Wattson-lookalike risk with FREE-WILi judges. Lead the pitch with the agent and the IR action, not the device. Keep a software simulator ready as a fallback.
- Keep the sponsor-specific build at or under about 26 h: core ≈22 h plus Figma ≈3.5 h. Capital One is only a substitute for FREE-WILi, never an addition.

#### Statement

##### Sponsor-track rep, round 2: I'm switching to the energy design, but it needs a better satellite feed

*Scope: I re-read files 13, 07, 04 (FREE-WILi) and 07 (SpaceX), and ran three new checks today. As the relayed user note asked, I skipped the second 2020 item and used no 2020-dated material.*

###### 1. I concede the project shape to "Clean Hours"
In round 1 I defended Overpass on sponsor grounds. That argument fails once FREE-WILi is counted. The energy-action design wins on **sponsor** expected value as well as on the main track:

| Sponsor EV [inference; verdict figures from `13-debate-and-verdict.md` §3] | Overpass | Clean Hours (with the GOES fix in §2) |
|---|---|---|
| Fetch.ai | ≈$180 (action = email or calendar) | ≈$180+. A physical action is the most literal reading of "take meaningful action" ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)) |
| Relay | ≈$175 | ≈$175 (the call changes something on the table) |
| FREE-WILi | not entered | ≈$120–320. In 2025, 5 entrants and 2 winners ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539)); Wattson won both Greenprint and FREE-WILi ([Wattson](https://devpost.com/software/wattson-5btsyd)) |
| SpaceX | ≈$70 (≈12%) | ≈$45–60 (≈8–10%) |
| ElevenLabs + Figma | ≈$63 | ≈$63 |
| **Total** | **≈$490** | **≈$585–800** |

The main-track representative's +3 to +5 points (≈$75–125) is also inference. I accept the direction of that claim, not its precision. The newly published **Adherence to Theme** criterion ([Devpost](https://mhacks-2026.devpost.com/)) and the track text "rethink energy" ([Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)) both favour mitigation, and I said so myself in round 1.

###### 2. Where the main-track plan is wrong: NASA POWER isn't live
The main-track plan uses NASA POWER as SpaceX's "space data." I queried POWER's API for Ann Arbor today:
- The **daily** series ends **Sept 28**, five days ago.
- The **hourly** series has **no valid value since Aug 1** (both [probe](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-83.74&latitude=42.28&start=20260801&end=20261003&format=JSON)).

So a `solar_outlook` built on POWER is climatology. It can't drive a live decision, and a SpaceX judge who has seen NOVA-style rigor would treat it as decoration. On POWER alone I'd put SpaceX at ≈4–6%, below the main-track rep's 6–8% [inference].

**Fix: replace it with GOES-19, a satellite parked over the Americas that observes them continuously.**
- **Sunlight at the ground, measured from orbit.** NOAA's public bucket already holds today's file. The 12:00 UTC Downward Shortwave Radiation full-disk file was written at 12:17 UTC (`ABI-L2-DSRF`), so it was 17 minutes old when posted ([S3 listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-DSRF/2026/276/)).
- **Clouds every 5 minutes.** The clear-sky (cloud) mask over the continental US is refreshed every 5 minutes, about 4 minutes behind real time (`ABI-L2-ACMC`, [S3 listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2026/276/)).
- **Easy to read.** The full-disk sunlight file is on a simple 0.5° latitude/longitude grid, so finding Ann Arbor's value needs no map-projection maths ([NCEI](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC01524)). One person can wire it up in ≈2–3 h with Python's `xarray` [inference; I couldn't open the NetCDF file locally].
- **The pitch line:** "GOES-19 measured 610 W/m² on Ann Arbor 17 minutes ago. The clouds are clearing and MISO's grid is cleaner, so the agent is calling you." Space data now drives the decision.

**Caveat:** this is still Earth observation, and it has no orbit-propagation hedge. Eligibility therefore depends on the 4 PM SpaceXAI session ([schedule](https://www.mhacks.org/live)). **I accept the main-track rep's rule: if SpaceXAI says no, drop SpaceX and don't redesign.**

###### 3. Fun tracks: a middle position
- **Judged by an LLM.** All three of us agree. Use the four Devpost criteria as headers, plus "What we measured" and "Limitations." The Fetch README owner writes it from hour one.
- **Dumbest Idea: accept the fun rep's planned-and-gated approach, with a new joke.** "Wave at NOAA-21" doesn't carry over to an energy product. Instead, make the agent's persona the **Digital Garden itself: a melodramatic houseplant** that wilts when you run the dryer at peak and calls to guilt-trip you. Two Relay updates make this nearly free:
  - On 2026-10-01 Relay added **Rive characters drawn during calls**.
  - The same update shipped `@relaymessenger/elevenlabs`, which "answers calls with an ElevenLabs Agent and moves a Rive character's mouth with its voice" ([changelog](https://docs.relayapp.im/changelog.md)).

  That persona is work Relay and ElevenLabs reward anyway: Relay's workshop builds a character, and ElevenLabs scores personality. Dumbest Idea is a by-product of it, so I'm meeting the main rep's "don't build for it" halfway. Three guardrails:
  - Budget ≤1 h.
  - Go/no-go at midnight.
  - Keep the joke off ASI:One, because Fetch.ai weights Real-World Impact at 20%.

  Ask on Discord whether judges can see which fun tracks a team ticked.
- **Useless AI.** Skip it; all three of us agree.

###### 4. Final sponsor stack
| Core | Hours | Owner | Why it's real use, not a ticked box |
|---|---|---|---|
| Relay | ≈4 | P1 (iOS 26) | The agent calls the user, and the call can end with the fan turning off |
| ElevenLabs | ≈1 | P1 | The voice and lip-sync on every call (above). **Moved to core**: I concede to the fun rep |
| Fetch.ai | ≈7 | P3 | ASI:One intent → Review card → the FREE-WILi acts |
| FREE-WILi | ≈5 | P4 | IR learn and send, garden on the screen, a physical "I'm leaving" button ([IR example](https://github.com/freewili/freewili-python/blob/master/examples/send_ir.py)) |
| SpaceX | ≈5 | P2 | GOES-19 data, Cursor, and Grok Imagine for the garden renders |
| **Total** | **≈22** | | |

- **Optional (in order):**
  1. **Figma** (≈3.5 h, P4). This brings the total to ≈25.5 h, within the main rep's ≈26 h ceiling.
  2. **Capital One "Green Fund."** Build it *only* as a swap-in if FREE-WILi fails at 2 PM (the main rep's rule, which I accept).
  3. **Notability**, only with a free Pro code. Pro is $79.99 with no free trial ([pricing](https://notability.com/pricing)).
- **Not entered:**
  - SpacetimeDB: it must be the core of a multi-user product.
  - Neon: "fullest use" means branching, which this product doesn't need, and it conflicts with SpacetimeDB.
  - Photon: the fallback if Relay calls fail.
  - FinchNode: it pulls the pitch toward health.

###### 5. Gates
I adopt the main rep's schedule, plus one item: at noon, confirm access to a grid-carbon API. Access to Electricity Maps' MISO zone is unverified by me.
- **Noon:** a teammate has iOS 26, and FREE-WILi loaners are confirmed at the expo.
- **1 PM:** split the team. P1 goes to Relay and P4 goes to FREE-WILi; the two sessions clash ([schedule](https://www.mhacks.org/live)).
- **2 PM:** FREE-WILi smoke test.
- **4 PM:** SpaceXAI ruling on GOES data, and the Relay calls go/no-go. Relay's 2026-10-02 `422` change means calls only reach phones running a Relay build that can take them ([changelog](https://docs.relayapp.im/changelog.md)).
- **6 PM:** Fetch.ai works end to end.
- **Midnight:** decide on the comic persona.

###### 6. Still open
- **If FREE-WILi and Relay calls both fail by 4 PM**, Clean Hours loses both of its demo moments, and most of its edge over Overpass goes with them. Even then we keep the design, because switching that late costs more than it gains. The team should know the advantage is conditional.
- **Look-alike risk.** FREE-WILi judges saw Wattson, also an energy device, last year. Lead with the agent and the IR action, not the device.

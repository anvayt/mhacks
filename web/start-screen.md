# Start screen (P3)

Not part of `PLAN.md`. Built pieces are the black start screen and the About page. The sequence below is planned and not implemented yet.

## Built

- `/` is a black screen with one button: the existing house photo (`/hero/house.png`) and the word Start on a white background.
- `/about` keeps the explanatory screen, including the listing link or address field. Do not redesign About for this flow.

## Planned click sequence

1. **Sticker peel.** On Start, the house leaves as a sticker peeling off. Do not use a plain fade. Come back to this animation later.
2. The blue-to-red background slowly reappears.
3. A white loading bar fades in from the bottom.
4. When the bar finishes, bring up the address field from the first About screen.
5. After the Next button on that address or listing link, fade the bar out, then bring in the survey. Not built yet.
6. Survey controls follow `PLAN.md` §4 and the `/estimate` question shape (`id`, `text`, `options`). Windows: single pane or double pane. Floor: top, middle, or ground. Heating fuel and who pays it: natural gas, or heat included in the rent. The year of insulation or air-sealing work and this month's gas bill stay self-fill boxes with arrows that change the value by 1.
7. After Next on the survey, the form fades, the white loading bar rises from the bottom, fills, then lowers the same way. The ranking screen then reveals the score slowly. Next on that screen stays disabled until one second after the score has appeared, then opens a mock same-type peer bar chart. Blue bars are the lower annual cost and red bars are the higher cost. Advice is not designed yet.

## Game ideas to try next

These stay inside the rules already in `PLAN.md` §5: every number comes from the model, uncertain grades stay a span, and small landlords are not named.

- **Grade lock.** The survey is the game. Each answer narrows the span, and the grade locks only when P10–P90 sits inside one band.
- **Streak.** After move-in, a month below the weather-normal bill adds one to the streak from `/calibrate`. A miss resets it. Sign-in is what lets that streak survive a new browser.
- **Peer race.** The vertical bars are the bracket. Your bar moves when an answer or a fix changes the estimate, and the page gradient shifts with the same score.
- **Listing battle.** Two saved scores, same size, one winner. That is the compare view, not a new scoring rule.
- **Fix as a move.** The advice list is the next turn: each fix shows dollars, CO₂, and the grade it would unlock. Choosing one is the action. The write-up of that advice comes later.

The gradient split (more blue when the bill is below the bracket, more red when it is above) is a later gimmick. It follows the Hidden Rent Score in `PLAN.md` §5. Do not edit `PLAN.md` for this.

/** Mock same-type peers. Stands in for GET /leaderboard entries from the model. Not a live rank. */

const LOW_ANNUAL_USD = 1052;
const HIGH_ANNUAL_USD = 2254;
const COUNT = 9;

export type PeerEntry = {
  id: string;
  label: string;
  annualUsd: number;
  you: boolean;
};

export const mockPeers: PeerEntry[] = Array.from({ length: COUNT }, (_, index) => {
  const annualUsd = Math.round(LOW_ANNUAL_USD + (index * (HIGH_ANNUAL_USD - LOW_ANNUAL_USD)) / (COUNT - 1));
  const you = index === Math.floor(COUNT / 2);
  return {
    id: you ? "you" : `peer-${index + 1}`,
    label: you ? "You" : `Peer ${index + 1}`,
    annualUsd,
    you,
  };
});

/** Same stops as the page background: blue through 35%, red from 65%. */
export function backgroundColorAt(position: number) {
  const t = Math.min(1, Math.max(0, position));
  let mix = 0;
  if (t >= 0.65) mix = 1;
  else if (t > 0.35) mix = (t - 0.35) / 0.3;
  const from = [0x17, 0x3b, 0xfa];
  const to = [0xf2, 0x38, 0x33];
  const channel = from.map((value, index) => Math.round(value + (to[index] - value) * mix));
  return `rgb(${channel.join(", ")})`;
}

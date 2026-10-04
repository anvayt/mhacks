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

/** Even blend from brand blue at the low bill to brand red at the high bill. */
export function backgroundColorAt(position: number) {
  const mix = Math.min(1, Math.max(0, position));
  const from = [0x17, 0x3b, 0xfa];
  const to = [0xf2, 0x38, 0x33];
  const channel = from.map((value, index) => Math.round(value + (to[index] - value) * mix));
  return `rgb(${channel.join(", ")})`;
}

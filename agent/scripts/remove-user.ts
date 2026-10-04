// Remove an allowlisted phone from the Photon project: npm run remove-user -- +15551234567
// Use it to reset a phone and test the onboarding flow from scratch.
import { env } from "../src/env.ts";
import { normalizePhone, removeSharedUserByPhone } from "../src/photon.ts";

const phone = normalizePhone(process.argv[2] ?? "");
if (!phone) {
  console.error("usage: npm run remove-user -- +15551234567");
  process.exit(1);
}
if (!env.hasPhoton) {
  console.error("Set PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET in agent/.env first.");
  process.exit(1);
}
try {
  const removed = await removeSharedUserByPhone(env, phone);
  if (removed.length === 0) {
    console.log(`${phone} isn't allowlisted on this Photon project; nothing to remove. (npm run doctor lists who is.)`);
  } else {
    console.log(`removed ${phone} from the allowlist (user ${removed.map((u) => u.id).join(", ")}).`);
    console.log("That phone can now go through the onboarding page from scratch.");
  }
} catch (err) {
  // PhotonError messages carry Photon's status and message only, never the credentials.
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
}

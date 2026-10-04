// Preflight for the 10:30 PM checkpoint: npm run doctor
// Checks the Photon credentials and lists who is allowlisted (and which line each one texts).
import { env } from "../src/env.ts";
import { listSharedUsers } from "../src/photon.ts";

const FREE_PLAN_USERS = 10; // https://photon.codes/pricing

if (!env.hasPhoton) {
  console.error("✗ PHOTON_PROJECT_ID / PHOTON_PROJECT_SECRET not set in agent/.env (agent and onboarding will run on mocks).");
  process.exit(1);
}
try {
  const { users, total } = await listSharedUsers(env);
  console.log(`✓ Photon credentials work. ${total} allowlisted phone(s):`);
  for (const u of users) console.log(`  ${u.phoneNumber}  ${u.firstName ?? ""}  → texts ${u.assignedPhoneNumber}`);
  if (total >= FREE_PLAN_USERS) console.log(`! ${total}/${FREE_PLAN_USERS}: the free plan may be full; delete users in the dashboard to free slots.`);
  console.log(`Onboarding QR points at ${env.publicUrl}${env.publicUrl.includes("localhost") ? " (localhost: phones can't open this; set PUBLIC_URL to your tunnel)" : ""}`);
} catch (err) {
  console.error(`✗ ${err instanceof Error ? err.message : err}`);
  process.exit(1);
}

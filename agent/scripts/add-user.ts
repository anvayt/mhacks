// Allowlist a phone on the Photon project: npm run add-user -- +15551234567 [FirstName]
import { env } from "../src/env.ts";
import { createSharedUser, normalizePhone, redirectUrl } from "../src/photon.ts";

const [rawPhone, name] = process.argv.slice(2);
const phone = normalizePhone(rawPhone ?? "");
if (!phone) {
  console.error("usage: npm run add-user -- +15551234567 [FirstName]");
  process.exit(1);
}
if (!env.hasPhoton) {
  console.error("Set PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET in agent/.env first.");
  process.exit(1);
}
try {
  const user = await createSharedUser(env, phone, name);
  console.log(`allowlisted ${user.phoneNumber} (user ${user.id})`);
  console.log(`From that phone, text the agent at ${user.assignedPhoneNumber}`);
  console.log(`or open on the phone: ${redirectUrl(user.id)}`);
} catch (err) {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
}

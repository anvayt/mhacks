import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { env } from "./env.ts";
import { shareCard } from "./intro.ts";

/** Only called after terminal mode is ruled out. Space resolution does not create/allowlist a Photon user. */
export async function phoneTransport() {
  if (env.agentTerminal) throw new Error("Phone transport is disabled in terminal mode.");
  const app = await Spectrum({ projectId: env.projectId, projectSecret: env.projectSecret, providers: [imessage.config()] });
  return {
    app,
    send: async (handle: string, text: string) => { const space = await imessage(app).space.create(handle); await space.send(text); },
    sendCard: async (handle: string, line?: string | null) => shareCard(await imessage(app).space.create(handle), line),
  };
}

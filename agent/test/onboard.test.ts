import assert from "node:assert/strict";
import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { after, before, test } from "node:test";
import { createHandler, type Register } from "../src/onboard.ts";

let server: Server;
let base = "";
const registered: string[] = [];
const register: Register = async (phone) => {
  if (phone === "+17345550000") throw new Error("maxSharedUsers");
  registered.push(phone);
  return { id: "user-123", phoneNumber: phone };
};

before(async () => {
  server = createServer(createHandler(register, false, "https://hiddenrent.example"));
  await new Promise<void>((r) => server.listen(0, r));
  base = `http://localhost:${(server.address() as AddressInfo).port}`;
});
after(() => server.close());

const join = (phone: string) =>
  fetch(`${base}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ phone, name: "Ada" }),
    redirect: "manual",
  });

test("GET / serves the phone form", async () => {
  const res = await fetch(base);
  assert.equal(res.status, 200);
  assert.match(await res.text(), /<form method="post" action="\/join">/);
});

test("POST /join allowlists the number and redirects into Photon's deep link", async () => {
  const res = await join("(734) 555-0123");
  assert.equal(res.status, 302);
  assert.match(res.headers.get("location")!, /^https:\/\/spectrum\.photon\.codes\/users\/user-123\/redirect\?msg=/);
  assert.deepEqual(registered, ["+17345550123"]);
});

test("POST /join rejects a bad number without calling Photon", async () => {
  const before = registered.length;
  const res = await join("12345");
  assert.equal(res.status, 400);
  assert.equal(registered.length, before);
});

test("POST /join shows a friendly error when Photon refuses", async () => {
  const res = await join("734-555-0000");
  assert.equal(res.status, 502);
  assert.match(await res.text(), /Ask us at the table/);
});

test("GET /qr.svg returns an SVG QR code", async () => {
  const res = await fetch(`${base}/qr.svg`);
  assert.equal(res.headers.get("content-type"), "image/svg+xml");
  assert.match(await res.text(), /^<svg/);
});

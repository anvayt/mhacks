import { gradeLabel, money, annualRange, billLabel, buildingLine, hiddenRent, carbon, peerLabel, type Estimate } from "@/components/hidden-rent-map/estimate-data";
import { qrMatrix } from "./qr";

export async function shareImage(e: Estimate, url: string): Promise<Blob> {
  await document.fonts.ready;
  const canvas = document.createElement("canvas"); canvas.width = 1200; canvas.height = 1400;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("This browser cannot create a PNG. Try another browser.");
  const font = (family: string) => getComputedStyle(document.documentElement).getPropertyValue(family).trim() || "sans-serif";
  const sans = font("--font-sans"), display = font("--font-display"), mono = font("--font-mono");
  ctx.fillStyle = "#173bfa"; ctx.fillRect(0,0,1200,1400);
  ctx.fillStyle = "#f4f2eb"; ctx.fillRect(40,40,1120,1320);
  ctx.fillStyle = "#11121a";
  const text = (value: string, x: number, y: number, size: number, family = sans) => { ctx.font = `${size}px ${family}`; ctx.fillText(value,x,y); };
  text("HIDDEN RENT / ANN ARBOR",90,112,24,mono);
  text(billLabel(e),90,170,22,mono);
  const address = e.building.address;
  ctx.font = `36px ${display}`;
  const addressLines: string[] = []; let line = "";
  for (const word of address.split(" ")) { const next = line ? `${line} ${word}` : word; if (ctx.measureText(next).width > 1000 && line) { addressLines.push(line); line = word; } else line = next; }
  addressLines.push(line);
  addressLines.slice(0,2).forEach((v,i) => text(v,90,230+i*44,36,display));
  text(gradeLabel(e),90,550,260,display);
  text(e.locked === false ? `Point grade ${e.grade} · answer-dependent range` : "Predicted efficiency grade",90,610,25,mono);
  text(peerLabel(e),90,668,27,sans);
  ctx.fillRect(90,708,1020,2);
  text(`${money(e.bill.annual.p50)}/year`,90,800,68,display);
  text(`${annualRange(e)} · estimated range`,90,850,25,mono);
  const building = buildingLine(e);
  if (building) text(building,90,884,20,mono);
  text(`${hiddenRent(e)} hidden rent`,90,930,44,display);
  text("Compared with the same-type median",90,971,24,sans);
  text(`${carbon(e)} · predicted`,90,1044,36,display);
  if (e.bill.note) {
    ctx.font = `19px ${sans}`; const lines: string[] = []; let line = "";
    for (const word of e.bill.note.split(" ")) { const next = line ? `${line} ${word}` : word; if (ctx.measureText(next).width > 1000 && line) { lines.push(line); line = word; } else line = next; }
    lines.push(line); lines.slice(0,2).forEach((v,i) => text(v,90,1080+i*24,19,sans));
  }
  const qr = qrMatrix(url), cell = Math.floor(236 / qr.size), side = qr.size * cell, x = 880, y = 1122;
  ctx.fillStyle = "#fff"; ctx.fillRect(x,y,side,side); ctx.fillStyle = "#11121a";
  for (const [col,row] of qr.cells) ctx.fillRect(x+col*cell,y+row*cell,cell,cell);
  text("CHECK YOURS ↗",90,1170,34,display);
  text(new URL(url).host,90,1217,25,mono);
  text("Typical weather. Not a bill. Rent + other utilities excluded.",90,1305,20,sans);
  return new Promise((resolve,reject) => canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("PNG export failed. Try again.")), "image/png"));
}

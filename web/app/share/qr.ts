import qrcode from "qrcode-generator";

// Four-module quiet zone is required for reliable scanning in both SVG and PNG.
export function qrMatrix(url: string) {
  const qr = qrcode(0, "M");
  qr.addData(url); qr.make();
  const modules = qr.getModuleCount();
  const cells: [number, number][] = [];
  for (let row = 0; row < modules; row++) for (let col = 0; col < modules; col++) {
    if (qr.isDark(row, col)) cells.push([col + 4, row + 4]);
  }
  return { size: modules + 8, cells };
}

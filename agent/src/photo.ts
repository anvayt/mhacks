// Bill photos: iPhones send HEIC, which many vision models don't read. Convert to JPEG when we can.
// heif2jpeg is an optional native dependency; if it's missing or fails, send the original bytes.

const isHeic = (mimeType: string, name = "") => /hei[cf]/i.test(mimeType) || /\.hei[cf]$/i.test(name);

export async function billImageBase64(bytes: Buffer, mimeType: string, name?: string): Promise<string> {
  if (isHeic(mimeType, name)) {
    try {
      const { heifToJpeg } = (await import("heif2jpeg")) as { heifToJpeg: (b: Buffer, o?: { quality?: number }) => Promise<Buffer> };
      return (await heifToJpeg(bytes, { quality: 85 })).toString("base64");
    } catch (err) {
      console.warn(`HEIC → JPEG failed, sending the original photo: ${err instanceof Error ? err.message : err}`);
    }
  }
  return bytes.toString("base64");
}

// Reproducible PNG icons. Artwork stays within the maskable safe zone.
import { deflateSync } from "node:zlib";
import { mkdirSync, writeFileSync } from "node:fs";
function crc32(data) {
  let crc = 0xffffffff;
  for (const byte of data) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++)
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const name = Buffer.from(type);
  const size = Buffer.alloc(4);
  size.writeUInt32BE(data.length);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([name, data])));
  return Buffer.concat([size, name, data, crc]);
}
function icon(size) {
  const pixels = Buffer.alloc(size * (1 + size * 3));
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const dx = x / size - 0.5,
        dy = y / size - 0.5;
      const planet = dx * dx + dy * dy < 0.048;
      const ring =
        Math.abs(
          Math.hypot(
            (dx * 0.87 - dy * 0.5) / 0.34,
            (dx * 0.5 + dy * 0.87) / 0.11,
          ) - 1,
        ) < 0.023;
      const star = Math.abs(dx - 0.22) + Math.abs(dy + 0.23) < 0.032;
      const color =
        ring || star
          ? [225, 233, 195]
          : planet
            ? [210, 162, 119]
            : [24, 43, 42];
      const offset = y * (1 + size * 3) + 1 + x * 3;
      pixels.set(color, offset);
    }
  const header = Buffer.alloc(13);
  header.writeUInt32BE(size);
  header.writeUInt32BE(size, 4);
  header[8] = 8;
  header[9] = 2;
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", header),
    chunk("IDAT", deflateSync(pixels)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}
mkdirSync("public/icons", { recursive: true });
for (const size of [192, 512])
  writeFileSync(`public/icons/luma-${size}.png`, icon(size));
writeFileSync("public/icons/luma-maskable-512.png", icon(512));
writeFileSync("app/apple-icon.png", icon(180));

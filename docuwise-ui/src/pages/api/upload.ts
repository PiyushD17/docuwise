import type { NextApiRequest, NextApiResponse } from "next";
import { parseJsonSafe } from "@/lib/safeJson";

export const config = {
  api: { bodyParser: false }, // important: pass raw stream for multipart
};

const BASE_URL =
  process.env.API_BASE_URL_INTERNAL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000";
// TEMP DEBUG
console.log("[API ROUTE] Using BASE_URL:", BASE_URL);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const chunks: Buffer[] = [];
    for await (const chunk of req) chunks.push(chunk as Buffer);
    const bodyBuffer = Buffer.concat(chunks);
    const contentType = req.headers["content-type"] || "application/octet-stream";

    const upstream = await fetch(`${BASE_URL}/api/upload`, {
      method: "POST",
      headers: {
        "Content-Type": Array.isArray(contentType) ? contentType[0] : contentType,
      },
      body: bodyBuffer,
    });

    const text = await upstream.text();
    const json = parseJsonSafe<unknown>(text);

    if (!upstream.ok) {
      const maybeObj = (json && typeof json === "object") ? (json as Record<string, unknown>) : null;
      const msg =
        (maybeObj?.error && typeof maybeObj.error === "string" && maybeObj.error) ||
        (maybeObj?.message && typeof maybeObj.message === "string" && maybeObj.message) ||
        `Upstream error (${upstream.status})`;
      return res.status(upstream.status).json({ error: msg });
    }

    return res.status(200).send(json ?? text);
  } catch {
    return res.status(502).json({ error: "Network error contacting backend." });
  }
}

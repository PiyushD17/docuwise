import type { NextApiRequest, NextApiResponse } from "next";

// function errorMessage(e: unknown, prefix = "Proxy failed"): string {
//   if (e instanceof Error) return `${prefix}: ${e.message}`;
//   if (typeof e === "string") return `${prefix}: ${e}`;
//   return `${prefix}.`;
// }

// export default async function handler(req: NextApiRequest, res: NextApiResponse) {
//   const { id } = req.query as { id: string };
//   const backend = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
//   const basePath = process.env.BACKEND_FILES_PATH || "/api/files";

function errorMessage(e: unknown, prefix = "Proxy failed"): string {
  if (e instanceof Error) return `${prefix}: ${e.message}`;
  if (typeof e === "string") return `${prefix}: ${e}`;
  return `${prefix}.`;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query as { id: string };
  const BASE_URL =
    process.env.API_BASE_URL_INTERNAL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000";
  const basePath = process.env.BACKEND_FILES_PATH || "/api/files";

  try {
    const url = `${BASE_URL}${basePath}/${encodeURIComponent(id)}/status`;
    console.log("[STATUS PROXY] ->", url);
    const r = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    const ct = r.headers.get("content-type") || "";
    if (!r.ok || !ct.includes("application/json")) {
      const text = await r.text();
      return res.status(r.status).json({ error: `Backend error ${r.status}`, body: text.slice(0, 200) });
    }
    const data = await r.json();
    res.status(200).json(data);
  } catch (e: unknown) {
    res.status(500).json({ error: errorMessage(e) });
  }
}

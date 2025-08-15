import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const backend = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const path = process.env.BACKEND_FILES_PATH || "/api/files";
  const limit = (req.query.limit as string) || "10";

  try {
    const r = await fetch(`${backend}${path}?limit=${encodeURIComponent(limit)}`, {
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
  } catch (e: any) {
    res.status(500).json({ error: `Proxy failed: ${e.message}` });
  }
}

import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const backend = process.env.NEXT_PUBLIC_API_BASE_URL;        // http://api:8000 (Docker) or http://localhost:8000
  const path = process.env.BACKEND_QUERY_PATH || "/api/query"; // set this to your real route
  if (!backend) return res.status(500).json({ error: "NEXT_PUBLIC_API_BASE_URL not set" });

  try {
    const upstream = await fetch(`${backend}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body || {}),
    });

    const contentType = upstream.headers.get("content-type") || "application/json";
    const text = await upstream.text();
    res.status(upstream.status).setHeader("Content-Type", contentType).send(text);
  } catch (e) {
    console.error(e);
    res.status(502).json({ error: "Query proxy failed to reach backend" });
  }
}

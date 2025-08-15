// src/pages/api/uploads.ts
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  const backend = process.env.NEXT_PUBLIC_API_BASE_URL; // e.g., http://api:8000 (Docker) or http://localhost:8000
  try {
    if (!backend) throw new Error("NEXT_PUBLIC_API_BASE_URL not set");

    const r = await fetch(`${backend}/api/uploads`, { cache: "no-store", headers: { Accept: "application/json" } });

    // If backend returns HTML (404 page), don’t forward it to the client UI
    const ct = r.headers.get("content-type") || "";
    if (!r.ok || ct.includes("text/html")) {
      throw new Error(`Backend responded ${r.status} for /api/uploads`);
    }

    const data = await r.json();
    res.status(200).json(data);
  } catch (e) {
    // Fallback mock so the UI still works until your backend endpoint exists
    res.status(200).json({
      items: [
        {
          id: "demo1",
          filename: "sample.pdf",
          size: 2 * 1024 * 1024,
          uploaded_at: new Date().toISOString(),
          status: "done",
        },
      ],
    });
  }
}

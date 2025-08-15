import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });
  const backend = process.env.NEXT_PUBLIC_API_BASE_URL;
  try {
    const r = await fetch(`${backend}/query`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(req.body || {}) });
    if (!r.ok) throw new Error(await r.text());
    const data = await r.json();
    res.status(200).json(data);
  } catch {
    res.status(200).json({ answer: "(stub) Query API not ready yet." });
  }
}

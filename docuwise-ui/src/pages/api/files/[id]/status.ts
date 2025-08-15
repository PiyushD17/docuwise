import type { NextApiRequest, NextApiResponse } from "next";
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query;
  const backend = process.env.NEXT_PUBLIC_API_BASE_URL;
  try {
    const r = await fetch(`${backend}/files/${id}/status`, { cache: "no-store" });
    const data = await r.json();
    res.status(r.ok ? 200 : r.status).json(data);
  } catch {
    res.status(200).json({ status: "processing" });
  }
}

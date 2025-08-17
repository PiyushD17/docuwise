// src/pages/api/hello.ts
import type { NextApiRequest, NextApiResponse } from "next";

type HelloOk = { name: string };
type ApiError = { error: string };

export default function handler(
  _req: NextApiRequest,
  res: NextApiResponse<HelloOk | ApiError>
) {
  res.status(200).json({ name: "DocuWise" });
}

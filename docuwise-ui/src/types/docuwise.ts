// src/types/docuwise.ts
export type ISODateString = string;

export interface FileMeta {
  id: string;            // backend _id mapped to string
  filename: string;
  size: number;          // bytes
  uploadTime: ISODateString; // e.g., "2025-08-15T19:12:00Z"
  status?: "queued" | "processing" | "indexed" | "failed";
}

export interface SourceChunk {
  docId: string;
  page?: number;
  snippet?: string;
}

export interface QueryResponse {
  answer: string;
  sources?: SourceChunk[];
}

export interface FileListResponse {
  files: FileMeta[];
}

export interface FileStatusResponse {
  id: string;
  status: NonNullable<FileMeta["status"]>;
  lastUpdated: ISODateString;
}

export interface ApiError {
  error: string;
}

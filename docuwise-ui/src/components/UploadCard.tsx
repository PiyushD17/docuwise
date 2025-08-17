// src/components/UploadCard.tsx
"use client";

import React from "react";
import Spinner from "./Spinner";
import { useToast } from "./Toast";

type UploadState = "idle" | "uploading" | "success" | "error";
type ProcessingState = "idle" | "queued" | "processing" | "done" | "failed";
type UploadResult = { ok: boolean; id?: string; error?: string };

const ALLOWED_MIME = new Set([
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]);
const MAX_SIZE_MB = 50;
const bytesToMB = (b: number) => (b / (1024 * 1024)).toFixed(2);

export default function UploadCard() {
  const [dragActive, setDragActive] = React.useState(false);
  const [file, setFile] = React.useState<File | null>(null);

  const [state, setState] = React.useState<UploadState>("idle");
  const [processing, setProcessing] = React.useState<ProcessingState>("idle");
  const [msg, setMsg] = React.useState("");
  const [progress, setProgress] = React.useState(0);

  const [uploadedId, setUploadedId] = React.useState<string | null>(null);

  const inputRef = React.useRef<HTMLInputElement | null>(null);
  const { push } = useToast();

  function validate(f: File) {
    if (!ALLOWED_MIME.has(f.type)) {
      return `Unsupported type: ${f.type || "unknown"} (PDF/DOCX only).`;
    }
    if (f.size / (1024 * 1024) > MAX_SIZE_MB) {
      return `File too large (${bytesToMB(f.size)} MB, max ${MAX_SIZE_MB} MB).`;
    }
    return null;
  }

  function onPick(f: File) {
    const err = validate(f);
    if (err) {
      setMsg(err);
      setState("error");
      setFile(null);
      return;
    }
    setFile(f);
    setState("idle");
    setMsg("");
    setProgress(0);
    setProcessing("idle");
    setUploadedId(null);
  }

  async function doUploadXHR() {
    if (!file) return;

    setState("uploading");
    setMsg("");
    setProgress(0);

    const form = new FormData();
    form.append("file", file);

    // Wrap XHR in a promise that never rejects
    const result: UploadResult = await new Promise<UploadResult>((resolve) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/upload");

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          setProgress(Math.round((e.loaded / e.total) * 100));
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          let id: string | undefined;
          try {
            const data = JSON.parse(xhr.responseText || "{}");
            id = data?.id || data?.file_id;
          } catch {
            // response wasn't JSON; ignore
          }
          resolve({ ok: true, id });
        } else {
          const error = xhr.responseText || `Upload failed (${xhr.status})`;
          resolve({ ok: false, error });
        }
      };

      xhr.onerror = () => {
        resolve({ ok: false, error: "Network error during upload." });
      };

      xhr.send(form);
    });

    if (!result.ok) {
      setState("error");
      setMsg(result.error || "Upload failed");
      push({ type: "error", message: "Upload failed" });
      return;
    }

    // Success path
    setState("success");
    setMsg("Upload successful. Starting processing…");
    push({ type: "success", message: "Upload complete" });

    const newId = result.id;
    if (newId) {
      setUploadedId(newId);
      setProcessing("queued");
      await pollStatus(newId);
    } else {
      // fallback demo when backend doesn't return an id
      setProcessing("processing");
      await new Promise((r) => setTimeout(r, 1200));
      setProcessing("done");
    }
  }

  async function pollStatus(_id: string) {
    setProcessing("processing");
    // Real polling example (uncomment and adapt when endpoint is ready):
    // try {
    //   const res = await fetch(`/api/files/${id}/status`, { cache: "no-store" });
    //   const data = await res.json();
    //   setProcessing((data?.status as ProcessingState) || "processing");
    // } catch {
    //   setProcessing("processing");
    // }

    // Demo fallback
    await new Promise((r) => setTimeout(r, 1500));
    setProcessing("done");
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">Upload a document</h2>
      <p className="mt-1 text-sm text-gray-600">PDF or DOCX up to {MAX_SIZE_MB} MB.</p>

      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragActive(false);
          const f = e.dataTransfer.files?.[0];
          if (f) onPick(f);
        }}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-10 text-center transition ${
          dragActive ? "border-indigo-400 bg-indigo-50" : "border-gray-300 bg-gray-50 hover:bg-gray-100"
        }`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-500" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7.5 21h9a2.25 2.25 0 0 0 2.25-2.25v-3.995a.75.75 0 0 0-1.5 0v3.995c0 .414-.336.75-.75.75h-9a.75.75 0 0 1-.75-.75v-3.995a.75.75 0 0 0-1.5 0v3.995A2.25 2.25 0 0 0 7.5 21Z" />
          <path d="M12 3a.75.75 0 0 0-.75.75v9.69L8.53 10.72a.75.75 0 1 0-1.06 1.06l4 4a.75.75 0 0 0 1.06 0l4-4a.75.75 0 1 0-1.06-1.06l-2.72 2.72V3.75A.75.75 0 0 0 12 3Z" />
        </svg>
        <div>
          <span className="font-medium text-gray-900">Drag &amp; drop</span>
          <span className="text-gray-600"> or click to browse</span>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onPick(f);
          }}
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="mt-2 rounded-full bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Choose file
        </button>
      </label>

      {file && (
        <div className="mt-4 flex items-center justify-between rounded-xl border bg-gray-50 p-3">
          <div>
            <p className="text-sm font-medium">{file.name}</p>
            <p className="text-xs text-gray-600">{bytesToMB(file.size)} MB</p>
          </div>
          <button
            type="button"
            onClick={() => setFile(null)}
            className="rounded-full px-3 py-1 text-xs text-gray-600 hover:bg-gray-200"
            disabled={state === "uploading"}
          >
            Remove
          </button>
        </div>
      )}

      <div className="mt-6 flex items-center gap-3">
        <button
          type="button"
          onClick={doUploadXHR}
          disabled={!file || state === "uploading"}
          className={`rounded-xl px-4 py-2 text-sm font-medium text-white transition ${
            !file || state === "uploading" ? "bg-gray-400" : "bg-indigo-600 hover:bg-indigo-500"
          }`}
        >
          {state === "uploading" ? "Uploading…" : "Upload"}
        </button>

        {state === "uploading" && (
          <div className="flex items-center gap-3">
            <div className="h-2 w-40 overflow-hidden rounded bg-gray-200">
              <div className="h-full rounded bg-indigo-500" style={{ width: `${progress}%` }} />
            </div>
            <span className="text-xs text-gray-600">{progress}%</span>
          </div>
        )}
      </div>

      {msg && (
        <div
          className={`mt-4 rounded-lg border p-3 text-sm ${
            state === "error"
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-700"
          }`}
        >
          {msg}
        </div>
      )}

      {/* Processing status strip */}
      {state === "success" && (
        <div className="mt-4 flex items-center justify-between rounded-lg border bg-white p-3">
          <div className="flex items-center gap-2 text-sm">
            {processing === "processing" && <Spinner />}
            <span className="font-medium">Status:</span>
            <span
              className={
                processing === "done"
                  ? "text-emerald-700"
                  : processing === "failed"
                  ? "text-red-700"
                  : "text-gray-700"
              }
            >
              {processing}
            </span>
          </div>
          <button
            type="button"
            onClick={() => uploadedId && pollStatus(uploadedId)}
            className="rounded-md border px-3 py-1 text-xs hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      )}
    </div>
  );
}

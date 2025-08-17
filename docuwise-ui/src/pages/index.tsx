import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading...");

    try {
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json()
        setStatus(`Upload successful! Saved as: ${data.saved_as}`);
      } else {
        setStatus("Upload failed.");
      }
    } catch (error) {
      console.error(error);
      setStatus("Error during upload.");
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white shadow-lg rounded-lg p-6">
        <div className="flex flex-col items-center space-y-4">
          <UploadIcon className="w-12 h-12 text-blue-500" />
          <h2 className="text-xl font-semibold">Upload a PDF</h2>

          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="file:mr-4 file:py-2 file:px-4 file:border-0
                       file:text-sm file:font-semibold
                       file:bg-blue-50 file:text-blue-700
                       hover:file:bg-blue-100"
          />

          <button
            onClick={handleUpload}
            disabled={status === "Uploading..."}
            className={`${
              status === "Uploading..." ? "opacity-50 cursor-not-allowed" : ""
            } bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded`}
          >
          Upload
        </button>

          {status && <p className="text-sm text-gray-600">{status}</p>}
        </div>
      </div>
    </main>
  );
}

function UploadIcon(props: React.ComponentProps<"svg">) {
  return (
    <svg
      {...props}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M7.5 12 12 7.5m0 0L16.5 12M12 7.5v9"
      />
    </svg>
  );
}

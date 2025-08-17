import React from "react";

export default function Spinner({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <div
      className={`inline-block animate-spin rounded-full border-2 border-current border-t-transparent align-[-0.125em] ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}

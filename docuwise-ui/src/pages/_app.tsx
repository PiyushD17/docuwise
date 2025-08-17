import type { AppProps } from "next/app";
import "../styles/globals.css";
import Link from "next/link";
import { ToastProvider } from "../components/Toast";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ToastProvider>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <header className="border-b bg-white">
          <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <Link href="/upload" className="text-lg font-semibold">
              DocuWise
            </Link>
            <ul className="flex items-center gap-4 text-sm">
              <li>
                <Link href="/upload" className="rounded px-3 py-1 hover:bg-gray-100">
                  Upload
                </Link>
              </li>
              <li>
                <Link href="/ask" className="rounded px-3 py-1 hover:bg-gray-100">
                  Ask
                </Link>
              </li>
            </ul>
          </nav>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-8">
          <Component {...pageProps} />
        </main>
      </div>
    </ToastProvider>
  );
}

// src/pages/_document.tsx
import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head />
      <body>
        <Main />
        {/* Portal target rendered on the server so hydration sees it */}
        <div id="toast-root" />
        <NextScript />
      </body>
    </Html>
  );
}

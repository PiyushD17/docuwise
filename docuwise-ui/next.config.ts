// import type { NextConfig } from "next";

// const nextConfig: NextConfig = {
//   /* config options here */
//   reactStrictMode: true,
// };

// export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig: import('next').NextConfig = {
  output: "standalone", // <-- makes .next/standalone for the COPY step
  reactStrictMode: true,// keep your existing config here
};

module.exports = nextConfig;

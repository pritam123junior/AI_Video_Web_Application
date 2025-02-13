import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // This rewrite ensures Clerk's routes (e.g., sign-in) work correctly
      {
        source: "/sign-in",
        destination: "/sign-in/[[...index]].js",
      },
      {
        source: "/sign-up",
        destination: "/sign-up/sign-up.js",
      },
    ];
  },
};

export default nextConfig;

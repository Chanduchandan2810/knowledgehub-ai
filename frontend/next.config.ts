import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.BACKEND_INTERNAL_URL || 'http://127.0.0.1:8000'}/api/v1/:path*`, // Proxy to Backend
      },
    ]
  },
};

export default nextConfig;

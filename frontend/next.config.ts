import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        has: [
          {
            type: 'cookie',
            key: 'demo_role',
          },
        ],
        destination: 'http://127.0.0.1:8000/api/v1/demo/:path*',
      },
      {
        source: '/api/v1/:path*',
        destination: 'http://127.0.0.1:8000/api/v1/:path*', // Proxy to Backend
      },
    ]
  },
};

export default nextConfig;

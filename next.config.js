/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/py/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002'}/api/:path*` // Proxy to FastAPI
      }
    ];
  }
};

module.exports = nextConfig; 
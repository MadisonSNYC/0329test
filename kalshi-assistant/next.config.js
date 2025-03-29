/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/py/:path*',
        destination: 'http://127.0.0.1:8000/:path*' // Proxy to FastAPI in dev
      }
    ];
  }
};

module.exports = nextConfig; 
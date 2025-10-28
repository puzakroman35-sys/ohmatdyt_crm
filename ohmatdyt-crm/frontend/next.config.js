/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || '/api',
  },

  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://api:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },

  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'http',
        hostname: 'nginx',
      },
    ],
  },

  webpack: (config) => {
    return config;
  },
};

module.exports = nextConfig;
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  poweredByHeader: false,
  eslint: { ignoreDuringBuilds: true },
  experimental: { optimizeCss: true },
};

export default nextConfig;

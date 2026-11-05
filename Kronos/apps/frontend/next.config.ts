
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Required for Docker optimization
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    unoptimized: true, // Often better for VPS without heavy CDN
  },
};

export default nextConfig;

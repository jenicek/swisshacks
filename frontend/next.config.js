/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable CORS for API requests
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
  // Support static exports for S3 hosting
  output: 'export',
  // When exporting, just use the API URL directly without rewrites
  // since CloudFront/S3 won't have rewrite capability
  distDir: 'out',
  images: {
    unoptimized: true, // Required for static export
  },
  trailingSlash: true, // Better for S3 static site hosting
}

module.exports = nextConfig
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Support static exports for S3 hosting
  output: 'export',
  // When exporting, just use the API URL directly
  // since CloudFront/S3 won't have rewrite capability
  distDir: 'out',
  images: {
    unoptimized: true, // Required for static export
  },
  trailingSlash: true, // Better for S3 static site hosting
  
  // Define environment variables for client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
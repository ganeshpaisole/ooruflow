/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
})

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '/api'
const apiProxyTarget = process.env.API_PROXY_TARGET?.replace(/\/$/, '')

const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: apiBaseUrl,
    NEXT_PUBLIC_RAZORPAY_KEY_ID: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || '',
    NEXT_PUBLIC_GMAPS_KEY: process.env.NEXT_PUBLIC_GMAPS_KEY || '',
  },
  async rewrites() {
    if (!apiProxyTarget || apiBaseUrl !== '/api') {
      return []
    }

    return [
      {
        source: '/api/:path*',
        destination: `${apiProxyTarget}/:path*`,
      },
    ]
  },
}
module.exports = withPWA(nextConfig)

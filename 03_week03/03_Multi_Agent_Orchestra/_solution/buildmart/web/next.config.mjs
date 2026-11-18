/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  experimental: {
    // ให้ pg / amqplib รันเป็น node module ปกติ (ไม่ bundle)
    serverComponentsExternalPackages: ['pg', 'amqplib'],
  },
};
export default nextConfig;

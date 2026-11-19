/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  serverExternalPackages: ['@node-rs/argon2', 'pg', 'busboy'],
};

export default nextConfig;

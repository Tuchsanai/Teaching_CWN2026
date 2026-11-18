/** @type {import('next').NextConfig} */
module.exports = {
  output: "standalone",
  experimental: { serverComponentsExternalPackages: ["sharp", "pg"] },
};

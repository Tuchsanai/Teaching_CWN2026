// ipv4-only.cjs — บังคับ Node ให้ใช้ IPv4 (แก้ npx playwright install ค้าง/timeout บนเครื่องที่ IPv6 ใช้ไม่ได้)
// ใช้:  $env:NODE_OPTIONS = "--require=$PWD\ipv4-only.cjs"; npx playwright install
const dns = require('dns');
const origLookup = dns.promises.lookup;
dns.promises.lookup = (hostname, options = {}) => {
  if (typeof options === 'object' && options.family === 6) return Promise.resolve([]);
  return origLookup.call(dns.promises, hostname, typeof options === 'object' ? { ...options, family: 4 } : 4);
};

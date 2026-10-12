// LAB 5: what did the browser really send to POST /api/orders? (reads out\bug01.har without opening it)
import { readFileSync } from 'node:fs';
const har = JSON.parse(readFileSync(process.argv[2] ?? 'out/bug01.har', 'utf8'));
const posts = har.log.entries.filter((e) => e.request.method === 'POST' && /\/api\/orders$/.test(e.request.url));
console.log('entries', har.log.entries.length, '· POST /api/orders', posts.length);
for (const e of posts) {
  const body = JSON.parse(e.request.postData?.text ?? '{}');
  const o = JSON.parse(e.response.content?.text ?? '{}').order ?? {};
  const { address, items, ...rest } = body;
  console.log(e.request.url, e.response.status, 'body keys=', Object.keys(body).join(','), '| non-item fields=', JSON.stringify(rest),
    '| items=', JSON.stringify(items), '| resp {subtotal,discount,shipping,total}=', [o.subtotal, o.discount, o.shipping, o.total].join(','));
}

// Screenshot of test/evidence/bug-hunt/index.html -> report.png (run from test/e2e)
const path = require('path'); const { pathToFileURL } = require('url');
const { chromium } = require(require.resolve('playwright-core', { paths: [path.dirname(require.resolve('@playwright/test', { paths: [process.cwd()] }))] }));
(async () => {
  const d = path.resolve(__dirname);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 1100 } });
  await p.goto(pathToFileURL(path.join(d, 'index.html')).href);
  await p.locator('details.tc.s-fail').first().evaluate(e => { e.open = true; });
  await p.screenshot({ path: path.join(d, 'report.png'), fullPage: false }); await b.close();
})();

// Screenshot of test/index.html -> test/evidence/test-report.png
// usage (from test/e2e so node_modules resolve): node ../../code_step15/shot_index.cjs
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require(require.resolve('playwright-core', { paths: [path.dirname(require.resolve('@playwright/test', { paths: [process.cwd()] }))] }));
(async () => {
  const root = path.resolve(__dirname, '..');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1000 } });
  await p.goto(pathToFileURL(path.join(root, 'test', 'index.html')).href);
  await p.locator('details.tc.s-fail').first().evaluate(e => { e.open = true; });
  await p.screenshot({ path: path.join(root, 'test', 'evidence', 'test-report.png'), fullPage: false });
  await b.close();
})();

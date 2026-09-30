## PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
isError=True
```text
### Error
Error: Browser "chrome-for-testing" is not installed; expected executable at /opt/ms-playwright/chromium-1247/chrome-linux64/chrome. Run `npx @playwright/mcp install-browser chrome-for-testing` to install
```
## PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
isError=None
```text
### Ran Playwright code
```js
await page.goto('https://example.com');
```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
- [Snapshot](out_p07/page-2026-09-30T05-05-59-264Z.yml)
```

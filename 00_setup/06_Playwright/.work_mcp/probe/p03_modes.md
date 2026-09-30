## yolo1_style
args: `--browser chromium --headless --isolated --no-sandbox --output-dir /workspace/.probe_mcp/out_v1`

### browser_navigate {"url": "https://example.com"}
bytes=293 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.goto('https://example.com');
```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
- [Snapshot](out_v1/page-2026-09-30T05-01-52-995Z.yml)
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=337 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.getByRole('link', { name: 'Learn more' }).click();
```
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
- [Snapshot](out_v1/page-2026-09-30T05-01-54-260Z.yml)
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=309 content=['text'] isError=None
```text
### Result
{
  "w": 1280,
  "h": 720,
  "dpr": 1,
  "lang": "en-US"
}
### Ran Playwright code
```js
await page.evaluate('() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})');
```
```
### browser_snapshot {}
bytes=6806 content=['text'] isError=None
```text
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
```yaml
- generic [active] [ref=f1e1]:
  - banner [ref=f1e2]:
    - generic [ref=f1e3]:
      - link [ref=f1e5] [cursor=pointer]:
        - /url: /
        - img "Homepage" [ref=f1e6]
      - generic [ref=f1e7]:
        - list:
          - listitem [ref=f1e8]:
            - link "Domains" [ref=f1e9] [cursor=pointer]:
              - /url: /domains
          - listitem [ref=f1e10]:
            - link "Protocols" [ref=f1e11] [cursor=pointer]:
              - /url: /protocols
          - listitem [ref=f1e12]:
            - link "Numbers" [ref=f1e13] [cursor=pointer]:
              - /url: /numbers
          - listitem [ref=f1e14]:
            - link "About" [ref=f1e15] [cursor=pointer]:
              - /url: /about
  - article [ref=f1e17]:
    - main [ref=f1e18]:
      - list [ref=f1e19
```
### browser_take_screenshot {"scale": "css"}
bytes=134071 content=['text', 'image'] isError=None
```text
### Result
- [Screenshot of viewport](out_v1/page-2026-09-30T05-01-54-807Z.png)
### Ran Playwright code
```js
// Screenshot viewport and save it as out_v1/page-2026-09-30T05-01-54-807Z.png
await page.screenshot({
  path: 'out_v1/page-2026-09-30T05-01-54-807Z.png',
  scale: 'css',
  type: 'png'
});
```
```
cwd files: playwright-artifacts-0802jB
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-KC88LZ
playwright-artifacts-TAZAxT
playwright-artifacts-Tu7qIr
playwright-artifacts-WGgHuf


## no_browser_flag
args: `--headless --isolated --no-sandbox`

### browser_navigate {"url": "https://example.com"}
bytes=241 content=['text'] isError=True
```text
### Error
Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=241 content=['text'] isError=True
```text
### Error
Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=241 content=['text'] isError=True
```text
### Error
Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```
### browser_snapshot {}
bytes=241 content=['text'] isError=True
```text
### Error
Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```
### browser_take_screenshot {"scale": "css"}
bytes=241 content=['text'] isError=True
```text
### Error
Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```
cwd files: playwright-artifacts-0802jB
playwright-artifacts-0B8dNb
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-BQxPk4
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-CBXL32
playwright-artifacts-KC88LZ


## no_output_dir
args: `--browser chromium --headless --isolated --no-sandbox`

### browser_navigate {"url": "https://example.com"}
bytes=302 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.goto('https://example.com');
```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
- [Snapshot](.playwright-mcp/page-2026-09-30T05-01-55-607Z.yml)
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=346 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.getByRole('link', { name: 'Learn more' }).click();
```
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
- [Snapshot](.playwright-mcp/page-2026-09-30T05-01-56-958Z.yml)
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=309 content=['text'] isError=None
```text
### Result
{
  "w": 1280,
  "h": 720,
  "dpr": 1,
  "lang": "en-US"
}
### Ran Playwright code
```js
await page.evaluate('() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})');
```
```
### browser_snapshot {}
bytes=6806 content=['text'] isError=None
```text
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
```yaml
- generic [active] [ref=f1e1]:
  - banner [ref=f1e2]:
    - generic [ref=f1e3]:
      - link [ref=f1e5] [cursor=pointer]:
        - /url: /
        - img "Homepage" [ref=f1e6]
      - generic [ref=f1e7]:
        - list:
          - listitem [ref=f1e8]:
            - link "Domains" [ref=f1e9] [cursor=pointer]:
              - /url: /domains
          - listitem [ref=f1e10]:
            - link "Protocols" [ref=f1e11] [cursor=pointer]:
              - /url: /protocols
          - listitem [ref=f1e12]:
            - link "Numbers" [ref=f1e13] [cursor=pointer]:
              - /url: /numbers
          - listitem [ref=f1e14]:
            - link "About" [ref=f1e15] [cursor=pointer]:
              - /url: /about
  - article [ref=f1e17]:
    - main [ref=f1e18]:
      - list [ref=f1e19
```
### browser_take_screenshot {"scale": "css"}
bytes=134098 content=['text', 'image'] isError=None
```text
### Result
- [Screenshot of viewport](.playwright-mcp/page-2026-09-30T05-01-57-506Z.png)
### Ran Playwright code
```js
// Screenshot viewport and save it as .playwright-mcp/page-2026-09-30T05-01-57-506Z.png
await page.screenshot({
  path: '.playwright-mcp/page-2026-09-30T05-01-57-506Z.png',
  scale: 'css',
  type: 'png'
});
```
```
cwd files: /workspace/.probe_mcp/.playwright-mcp
playwright-artifacts-0802jB
playwright-artifacts-0B8dNb
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-BQxPk4
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-CBXL32
playwright-artifacts-KC88LZ


## snapshot_none
args: `--browser chromium --headless --isolated --no-sandbox --snapshot-mode none --output-dir /workspace/.probe_mcp/out_v3`

### browser_navigate {"url": "https://example.com"}
bytes=223 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.goto('https://example.com');
```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=181 content=['text'] isError=True
```text
### Error
Error: Ref e13 not found in the current page snapshot. Try capturing new snapshot.
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=309 content=['text'] isError=None
```text
### Result
{
  "w": 1280,
  "h": 720,
  "dpr": 1,
  "lang": "en-US"
}
### Ran Playwright code
```js
await page.evaluate('() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})');
```
```
### browser_snapshot {}
bytes=1745 content=['text'] isError=None
```text
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
```yaml
- generic [active] [ref=e1]:
  - paragraph [ref=e7]: This domain is for use in documentation examples without needing permission. This is not a service, avoid relying on it for testing and monitoring purposes.
  - paragraph [ref=e8]: هذا النطاق مُخصص للاستخدام في أمثلة التوثيق دون الحاجة إلى إذن. هذه ليست خدمة، يُرجى تجنب الاعتماد عليها لأغراض الاختبار والمراقبة.
  - paragraph [ref=e9]: 该域名仅用于文档示例，无需获得许可。这并非一项服务，请勿将其用于测试和监控目的。
  - paragraph [ref=e10]: L’usage de ce domaine est réservé à des exemples de documentation, sans autorisation préalable. Il ne s’agit pas d’un service ; son utilisation à des fins de test ou de surveillance est à éviter.
  - paragraph [ref=e11]: Данный домен предназначен для использования в примерах документации без необходимости получения предварительного разрешения. Это не
```
### browser_take_screenshot {"scale": "css"}
bytes=28459 content=['text', 'image'] isError=None
```text
### Result
- [Screenshot of viewport](out_v3/page-2026-09-30T05-01-58-630Z.png)
### Ran Playwright code
```js
// Screenshot viewport and save it as out_v3/page-2026-09-30T05-01-58-630Z.png
await page.screenshot({
  path: 'out_v3/page-2026-09-30T05-01-58-630Z.png',
  scale: 'css',
  type: 'png'
});
```
```
cwd files: /workspace/.probe_mcp/.playwright-mcp
playwright-artifacts-0802jB
playwright-artifacts-0B8dNb
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-BQxPk4
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-CBXL32
playwright-artifacts-KC88LZ


## snapshot_boxes
args: `--browser chromium --headless --isolated --no-sandbox --snapshot-boxes --output-dir /workspace/.probe_mcp/out_v4`

### browser_navigate {"url": "https://example.com"}
bytes=293 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.goto('https://example.com');
```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
- [Snapshot](out_v4/page-2026-09-30T05-01-59-221Z.yml)
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=337 content=['text'] isError=None
```text
### Ran Playwright code
```js
await page.getByRole('link', { name: 'Learn more' }).click();
```
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
- [Snapshot](out_v4/page-2026-09-30T05-02-00-541Z.yml)
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=309 content=['text'] isError=None
```text
### Result
{
  "w": 1280,
  "h": 720,
  "dpr": 1,
  "lang": "en-US"
}
### Ran Playwright code
```js
await page.evaluate('() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})');
```
```
### browser_snapshot {}
bytes=8799 content=['text'] isError=None
```text
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
```yaml
- generic [active] [ref=f1e1] [box=0,0,1280,910]:
  - banner [ref=f1e2] [box=0,0,1280,128]:
    - generic [ref=f1e3] [box=40,0,1200,127]:
      - link [ref=f1e5] [cursor=pointer] [box=90,80,234,22]:
        - /url: /
        - img "Homepage" [ref=f1e6] [box=90,25,234,72]
      - generic [ref=f1e7] [box=873,25,317,38]:
        - list [box=873,41,317,0]:
          - listitem [ref=f1e8] [box=873,41,83,22]:
            - link "Domains" [ref=f1e9] [cursor=pointer] [box=877,37,79,30]:
              - /url: /domains
          - listitem [ref=f1e10] [box=956,41,86,22]:
            - link "Protocols" [ref=f1e11] [cursor=pointer] [box=960,37,82,30]:
              - /url: /protocols
          - listitem [ref=f1e12] [box=1042,41,86,22]:
            - link "Numbers" [ref=f1e13] [cursor=po
```
### browser_take_screenshot {"scale": "css"}
bytes=134071 content=['text', 'image'] isError=None
```text
### Result
- [Screenshot of viewport](out_v4/page-2026-09-30T05-02-01-105Z.png)
### Ran Playwright code
```js
// Screenshot viewport and save it as out_v4/page-2026-09-30T05-02-01-105Z.png
await page.screenshot({
  path: 'out_v4/page-2026-09-30T05-02-01-105Z.png',
  scale: 'css',
  type: 'png'
});
```
```
cwd files: /workspace/.probe_mcp/.playwright-mcp
playwright-artifacts-0802jB
playwright-artifacts-0B8dNb
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-BQxPk4
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-CBXL32
playwright-artifacts-KC88LZ


## codegen_none_imgomit
args: `--browser chromium --headless --isolated --no-sandbox --codegen none --image-responses omit --output-dir /workspace/.probe_mcp/out_v5`

### browser_navigate {"url": "https://example.com"}
bytes=215 content=['text'] isError=None
```text
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
- [Snapshot](out_v5/page-2026-09-30T05-02-01-757Z.yml)
```
### browser_click {"target": "e13", "element": "Learn more"}
bytes=237 content=['text'] isError=None
```text
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
- [Snapshot](out_v5/page-2026-09-30T05-02-03-010Z.yml)
```
### browser_evaluate {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}
bytes=158 content=['text'] isError=None
```text
### Result
{
  "w": 1280,
  "h": 720,
  "dpr": 1,
  "lang": "en-US"
}
```
### browser_snapshot {}
bytes=6806 content=['text'] isError=None
```text
### Page
- Page URL: https://www.iana.org/help/example-domains
- Page Title: Example Domains
### Snapshot
```yaml
- generic [active] [ref=f1e1]:
  - banner [ref=f1e2]:
    - generic [ref=f1e3]:
      - link [ref=f1e5] [cursor=pointer]:
        - /url: /
        - img "Homepage" [ref=f1e6]
      - generic [ref=f1e7]:
        - list:
          - listitem [ref=f1e8]:
            - link "Domains" [ref=f1e9] [cursor=pointer]:
              - /url: /domains
          - listitem [ref=f1e10]:
            - link "Protocols" [ref=f1e11] [cursor=pointer]:
              - /url: /protocols
          - listitem [ref=f1e12]:
            - link "Numbers" [ref=f1e13] [cursor=pointer]:
              - /url: /numbers
          - listitem [ref=f1e14]:
            - link "About" [ref=f1e15] [cursor=pointer]:
              - /url: /about
  - article [ref=f1e17]:
    - main [ref=f1e18]:
      - list [ref=f1e19
```
### browser_take_screenshot {"scale": "css"}
bytes=153 content=['text'] isError=None
```text
### Result
- [Screenshot of viewport](out_v5/page-2026-09-30T05-02-03-556Z.png)
```
cwd files: /workspace/.probe_mcp/.playwright-mcp
playwright-artifacts-0802jB
playwright-artifacts-0B8dNb
playwright-artifacts-55qcn3
playwright-artifacts-6pYepR
playwright-artifacts-AcQJvG
playwright-artifacts-BQxPk4
playwright-artifacts-Bcp1Cp
playwright-artifacts-BpfUMy
playwright-artifacts-CBXL32
playwright-artifacts-KC88LZ



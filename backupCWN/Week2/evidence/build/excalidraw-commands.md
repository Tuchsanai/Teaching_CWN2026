# Excalidraw production record

Commands below transcribe the commands executed in this build (not a fabricated raw terminal capture). CLI version/help: tool-help/excalidraw-help.txt. Canvas was initially empty at http://127.0.0.1:3017; started as an owned detached process. Browser client connected through instructor/runtime/diagram_browser.cjs using the installed Chromium.

```bash
excalidraw-canvas start --url http://127.0.0.1:3017
excalidraw-canvas describe --url http://127.0.0.1:3017
excalidraw-canvas add Week2/diagrams/workflow-elements.json --url http://127.0.0.1:3017
excalidraw-canvas export --out Week2/diagrams/workflow.excalidraw --url http://127.0.0.1:3017
excalidraw-canvas screenshot --format svg --out Week2/diagrams/workflow.svg --url http://127.0.0.1:3017
excalidraw-canvas screenshot --out Week2/diagrams/workflow.png --url http://127.0.0.1:3017
excalidraw-canvas snapshot save week2-workflow --url http://127.0.0.1:3017
excalidraw-canvas clear --yes --url http://127.0.0.1:3017
excalidraw-canvas add Week2/diagrams/workflow-mobile-elements.json --url http://127.0.0.1:3017
excalidraw-canvas export --out Week2/diagrams/workflow-mobile.excalidraw --url http://127.0.0.1:3017
excalidraw-canvas screenshot --format svg --out Week2/diagrams/workflow-mobile.svg --url http://127.0.0.1:3017
excalidraw-canvas screenshot --out Week2/diagrams/workflow-mobile.png --url http://127.0.0.1:3017
```

Horizontal exported PNG and actual rendered slide were opened for inspection. Horizontal diagram was too small on a 390 px viewport; a real vertical Excalidraw variant was created and exported. Final mobile PNG and slide screenshot were opened and inspected. Thai marks were visible; labels fit inside boxes, arrows connected adjacent stages. Exported editable text relies on the destination's font fallback; no universal font-rendering guarantee is claimed. Offline slide request audit confirms no external asset fetches.

Desktop element creation timestamp recorded by CLI: 2026-09-12T13:33:27.660Z. Mobile raw CLI create output is excalidraw-mobile-create.json and includes 2026-09-12 UTC timestamps.

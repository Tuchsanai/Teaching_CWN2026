| # | tool | required | properties | readOnlyHint/destructiveHint | description (บรรทัดแรก) |
|---|---|---|---|---|---|
| 1 | `browser_close` | - | - | False/True | Close the page |
| 2 | `browser_resize` | width, height | width, height | False/True | Resize the browser window |
| 3 | `browser_console_messages` | level | level, all, filename | True/False | Returns all console messages |
| 4 | `browser_handle_dialog` | accept | accept, promptText | False/True | Handle a dialog |
| 5 | `browser_emulate_media` | - | colorScheme, reducedMotion, forcedColors, contrast, media | False/True | Emulate CSS media features for the page, for example switch between the light and dark col |
| 6 | `browser_evaluate` | function | element, target, function, filename | False/True | Evaluate JavaScript expression on page or element |
| 7 | `browser_file_upload` | - | paths | False/True | Upload one or multiple files |
| 8 | `browser_drop` | target | element, target, paths, data | False/True | Drop files or MIME-typed data onto an element, as if dragged from outside the page. At lea |
| 9 | `browser_find` | - | text, regex, filename | True/False | Search the accessibility snapshot of the current page for text or a regular expression. Re |
| 10 | `browser_fill_form` | fields | fields | False/True | Fill multiple form fields |
| 11 | `browser_press_key` | key | key | False/True | Press a key on the keyboard |
| 12 | `browser_type` | target, text | element, target, text, submit, slowly | False/True | Type text into editable element |
| 13 | `browser_navigate` | url | url | False/True | Navigate to a URL |
| 14 | `browser_navigate_back` | - | - | False/True | Go back to the previous page in the history |
| 15 | `browser_network_requests` | static | static, filter, filename | True/False | Returns a numbered list of network requests since loading the page. Use browser_network_re |
| 16 | `browser_network_request` | index | index, part, filename | True/False | Returns full details (headers and body) of a single network request, or a single part if ` |
| 17 | `browser_run_code_unsafe` | - | code, filename | False/True | Run a Playwright code snippet. Unsafe: executes arbitrary JavaScript in the Playwright ser |
| 18 | `browser_take_screenshot` | scale | element, target, type, filename, fullPage, scale | True/False | Take a screenshot of the current page. You can't perform actions based on the screenshot,  |
| 19 | `browser_snapshot` | - | target, filename, depth, boxes | True/False | Capture accessibility snapshot of the current page, this is better than screenshot |
| 20 | `browser_click` | target | element, target, doubleClick, button, modifiers | False/True | Perform click on a web page |
| 21 | `browser_drag` | startTarget, endTarget | startElement, startTarget, endElement, endTarget | False/True | Perform drag and drop between two elements |
| 22 | `browser_hover` | target | element, target | False/True | Hover over element on page |
| 23 | `browser_select_option` | target, values | element, target, values | False/True | Select an option in a dropdown |
| 24 | `browser_tabs` | action | action, index, url | False/True | List, create, close, or select a browser tab. |
| 25 | `browser_wait_for` | - | time, text, textGone | True/False | Wait for text to appear or disappear or a specified time to pass |

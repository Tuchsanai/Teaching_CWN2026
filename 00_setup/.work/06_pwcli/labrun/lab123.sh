set -x
# LAB 1
cat > /usr/local/bin/playwright-cli <<'X'
#!/bin/sh
exec node "$(npm root -g)/@playwright/mcp/node_modules/playwright-core/lib/tools/cli-client/cli.js" "$@"
X
chmod +x /usr/local/bin/playwright-cli
playwright-cli --version
mkdir -p /workspace/.playwright && cd /workspace
cat > .playwright/cli.config.json <<'X'
{
  "outputDir": "/workspace/pwcli-out",
  "browser": {
    "browserName": "chromium",
    "launchOptions": { "chromiumSandbox": false },
    "contextOptions": { "viewport": { "width": 1920, "height": 1080 }, "deviceScaleFactor": 2, "locale": "en-US" }
  }
}
X
# LAB 2
playwright-cli open "https://www.google.com/travel/flights?hl=en"
playwright-cli snapshot --filename=flights.yml
grep -nE 'combobox|textbox|button "Search' flights.yml
playwright-cli find "ticket type"
REF=$(grep -o 'Change ticket type[^]]*ref=[a-z0-9]*' flights.yml | grep -o 'ref=.*' | cut -d= -f2)
playwright-cli click $REF
playwright-cli find "One way"
ONE=$(playwright-cli find "One way" | grep -o 'option "One way" \[ref=[a-z0-9]*' | grep -o 'ref=.*' | cut -d= -f2)
playwright-cli snapshot --boxes --filename=boxes.yml
grep -n 'option "One way"' boxes.yml
playwright-cli screenshot --hires --filename=lab2-dropdown.png
playwright-cli click $ONE
playwright-cli --raw eval "() => document.title"
# LAB 3 stale ref
playwright-cli click $REF
echo "exit=$?"
playwright-cli find "ticket type"
playwright-cli list
playwright-cli close
mkdir -p /out; cp *.png *.yml /out/

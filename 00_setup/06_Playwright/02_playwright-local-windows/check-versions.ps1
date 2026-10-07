# check-versions.ps1 — ขั้นที่ 1 + 2: ตรวจเวอร์ชันที่ติดตั้ง เทียบกับเวอร์ชันล่าสุด แล้วสรุปเป็นตาราง
# ใช้:  powershell -ExecutionPolicy Bypass -File .\check-versions.ps1 [-Project .\lab] [-Out log\versions-before.md]
# สคริปต์นี้ "อ่านอย่างเดียว" ไม่ติดตั้งหรืออัปเดตอะไรเลย
param(
  [string]$Project = (Join-Path $PSScriptRoot 'lab'),
  [string]$Out = ''
)
$ErrorActionPreference = 'SilentlyContinue'
$rows = @()

function Add-Row($name, $installed, $latest, $note = '') {
  if (-not $installed) { $status = 'ยังไม่ได้ติดตั้ง' }
  elseif (-not $latest) { $status = 'ตรวจล่าสุดไม่ได้' }
  else {
    try {
      $i = [version](($installed -replace '^v', '') -replace '[^0-9.].*$', '')
      $l = [version](($latest -replace '^v', '') -replace '[^0-9.].*$', '')
      $status = if ($i -ge $l) { 'ล่าสุดแล้ว' } else { 'ต้องอัปเดต' }
    } catch { $status = if ($installed -eq $latest) { 'ล่าสุดแล้ว' } else { 'ต้องอัปเดต' } }
  }
  $script:rows += [pscustomobject]@{ 'รายการ' = $name; 'ที่ติดตั้ง' = $installed; 'ล่าสุด' = $latest; 'สถานะ' = $status; 'หมายเหตุ' = $note }
}

# 1. Node.js — เทียบกับสายที่ติดตั้งอยู่ (LTS หรือ Current)
$node = (node -v)
$index = Invoke-RestMethod https://nodejs.org/dist/index.json
$lts = ($index | Where-Object { $_.lts } | Select-Object -First 1).version
$cur = $index[0].version
$wingetId = if ((winget list --id OpenJS.NodeJS.LTS -e 2>$null) -match 'OpenJS.NodeJS.LTS') { 'OpenJS.NodeJS.LTS' } else { 'OpenJS.NodeJS' }
if ($wingetId -eq 'OpenJS.NodeJS.LTS') { Add-Row 'Node.js' $node $lts "สาย LTS (winget: $wingetId)" }
else { Add-Row 'Node.js' $node $cur "สาย Current (winget: $wingetId) · LTS ล่าสุด $lts" }

# 2. npm
Add-Row 'npm' (npm -v) (npm view npm version)

# 3. Playwright MCP — ติดตั้ง global หรืออยู่ใน npx cache
$mcpLatest = npm view @playwright/mcp version
$mcpGlobal = ((npm ls -g @playwright/mcp --depth=0 2>$null) -join "`n") -replace '(?s).*@playwright/mcp@([0-9.]+).*', '$1'
if ($mcpGlobal -notmatch '^[0-9.]+$') { $mcpGlobal = $null }
$mcpNpx = Get-ChildItem "$env:LocalAppData\npm-cache\_npx" -Directory | ForEach-Object {
  $p = Join-Path $_.FullName 'node_modules\@playwright\mcp\package.json'
  if (Test-Path $p) { (Get-Content $p -Raw | ConvertFrom-Json).version } } | Sort-Object { [version]$_ } -Descending | Select-Object -First 1
Add-Row '@playwright/mcp (global)' $mcpGlobal $mcpLatest 'ไม่ติดตั้ง global ก็ได้ ถ้าเรียกผ่าน npx'
Add-Row '@playwright/mcp (npx cache)' $mcpNpx $mcpLatest '%LocalAppData%\npm-cache\_npx'

# 4. Playwright + เบราว์เซอร์ของ Playwright (ดูจากโปรเจกต์ lab)
$pwLatest = npm view playwright version
$pwInstalled = $null
if (Test-Path (Join-Path $Project 'package.json')) {
  Push-Location $Project
  $pwInstalled = ((npx --no-install playwright --version 2>$null) -replace 'Version\s*', '').Trim()
  Pop-Location
}
Add-Row '@playwright/test (lab)' $pwInstalled $pwLatest
$browsers = (Get-ChildItem "$env:LocalAppData\ms-playwright" -Directory -Name | Where-Object { $_ -match '^(chromium|firefox|webkit)' }) -join ', '
$rows += [pscustomobject]@{ 'รายการ' = 'เบราว์เซอร์ของ Playwright'; 'ที่ติดตั้ง' = $browsers; 'ล่าสุด' = '(ตาม playwright ในโปรเจกต์)'; 'สถานะ' = $(if ($browsers) { 'ดู npx playwright install --list' } else { 'ยังไม่ได้ติดตั้ง' }); 'หมายเหตุ' = '%LocalAppData%\ms-playwright' }

# 5. Google Chrome
$chrome = ((reg query 'HKCU\Software\Google\Chrome\BLBeacon' /v version 2>$null) -match 'version') -replace '.*REG_SZ\s+', ''
$chromeLatest = (Invoke-RestMethod https://versionhistory.googleapis.com/v1/chrome/platforms/win64/channels/stable/versions).versions[0].version
Add-Row 'Google Chrome' "$chrome".Trim() $chromeLatest

# 6. Microsoft Edge — winget บอกว่ามีรุ่นใหม่หรือไม่
$edge = ((reg query 'HKCU\Software\Microsoft\Edge\BLBeacon' /v version 2>$null) -match 'version') -replace '.*REG_SZ\s+', ''
$edgeUp = (winget upgrade --id Microsoft.Edge -e --accept-source-agreements 2>$null) -join "`n"
$edgeLatest = if ($edgeUp -match 'No available upgrade') { "$edge".Trim() } elseif ($edgeUp -match 'Microsoft\.Edge\s+\S+\s+(\S+)') { $Matches[1] } else { $null }
Add-Row 'Microsoft Edge' "$edge".Trim() $edgeLatest 'ล่าสุด = จาก winget upgrade'

# 7. Claude Code
$claude = ((claude --version) -replace '\s*\(.*', '').Trim()
$claudeLatest = npm view @anthropic-ai/claude-code version
Add-Row 'Claude Code' $claude $claudeLatest

$rows | Format-Table -AutoSize -Wrap | Out-String -Width 200 | Write-Host

# 8. npm outdated ในโปรเจกต์ (ถ้ามี package.json)
if (Test-Path (Join-Path $Project 'package.json')) {
  Push-Location $Project; Write-Host '--- npm outdated (lab) ---'; npm outdated; if ($LASTEXITCODE -eq 0) { Write-Host '(ทุกแพ็กเกจล่าสุดแล้ว)' }; Pop-Location
}

if ($Out) {
  $md = @('| รายการ | ที่ติดตั้ง | ล่าสุด | สถานะ | หมายเหตุ |', '|---|---|---|---|---|')
  $md += $rows | ForEach-Object { "| $($_.'รายการ') | $($_.'ที่ติดตั้ง') | $($_.'ล่าสุด') | $($_.'สถานะ') | $($_.'หมายเหตุ') |" }
  $md += '', "ตรวจเมื่อ $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
  $md | Out-File -Encoding utf8 $Out
  Write-Host "บันทึกตารางไว้ที่ $Out"
}

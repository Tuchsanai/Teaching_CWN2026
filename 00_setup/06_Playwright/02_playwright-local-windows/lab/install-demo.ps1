# install-demo.ps1 — ติดตั้ง Playwright Test ในโฟลเดอร์ lab แล้วรัน test (แสดงทุกคำสั่งบนจอ)
# ใช้:  powershell -ExecutionPolicy Bypass -File .\install-demo.ps1 [-IPv4]
#   -IPv4  บังคับ Node ใช้ IPv4 (ใช้เมื่อ npx playwright install ขึ้น "Download failure" เพราะ IPv6 ใช้ไม่ได้)
param([switch]$IPv4, [int]$PauseSec = 0)
Set-Location $PSScriptRoot
$env:NO_COLOR = $null; $env:FORCE_COLOR = $null; chcp 65001 > $null
function Run($cmd) { Write-Host "`nPS lab> $cmd" -ForegroundColor Cyan; cmd /c "$cmd 2>&1" | Out-Host; if ($PauseSec) { Start-Sleep $PauseSec } }
if ($IPv4) { $env:NODE_OPTIONS = "--require=$PSScriptRoot\ipv4-only.cjs"; Write-Host "NODE_OPTIONS=$env:NODE_OPTIONS" -ForegroundColor Yellow }
Run 'node -v'
Run 'npm -v'
if (-not (Test-Path package.json)) { Run 'npm init -y' }
Run 'npm install -D @playwright/test@latest'
Run 'npx playwright --version'
Run 'npx playwright install'
Run 'npx playwright install --list'
Run 'npx playwright test'
Write-Host "`nDone. Open the report with: npx playwright show-report" -ForegroundColor Green


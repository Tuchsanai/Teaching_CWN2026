<#
.SYNOPSIS
  เครื่องตรวจอัตโนมัติ ข้อสอบบท 06 (ชุด A / B) · Windows PowerShell 5.1 ขึ้นไป
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File grade.ps1 -Prep -Set B
  powershell -ExecutionPolicy Bypass -File grade.ps1 -Submission C:\exam\in\6501234.bundle -Set B -Variant 2
  powershell -ExecutionPolicy Bypass -File grade.ps1 -Submission C:\exam\in -Set B -All      # ทุก .bundle ในโฟลเดอร์ (variant จาก exam/VARIANT.json)
  powershell -ExecutionPolicy Bypass -File grade.ps1 -Cleanup -Images
#>
param(
  [string]$Submission,
  [ValidateSet('A', 'B', 'a', 'b')][string]$Set,
  [int]$Variant = -1,
  [string]$Id,
  [string]$Work = (Join-Path $env:USERPROFILE 'sabai-grader-work'),
  [string]$Out,
  [string]$Prefix = 'exref-g',
  [ValidateSet('full', 'quick', 'skip')][string]$E2E = 'full',
  [string]$Map,
  [switch]$All,
  [switch]$Prep,
  [switch]$Keep,
  [switch]$Cleanup,
  [switch]$Images
)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$grader = Join-Path $here 'grade.mjs'

function Assert-Tools {
  $nv = (& node -v) 2>$null
  if (-not $nv) { throw 'ไม่พบ node (ต้อง Node >= 22.18)' }
  $parts = $nv.TrimStart('v').Split('.')
  if ([int]$parts[0] -lt 22 -or ([int]$parts[0] -eq 22 -and [int]$parts[1] -lt 18)) { throw "Node $nv ต่ำกว่า 22.18" }
  & docker version --format '{{.Server.Version}}' | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop ยังไม่เปิด' }
  & git --version | Out-Null
}

function Invoke-Grader([string[]]$argv) {
  & node $grader @argv | Out-Host
  return $LASTEXITCODE
}

Assert-Tools
$common = @('--work', $Work, '--prefix', $Prefix)

if ($Cleanup) {
  $a = @('--cleanup') + $common
  if ($Images) { $a += '--images' }
  exit (Invoke-Grader $a)
}
if (-not $Set) { throw 'ต้องระบุ -Set A หรือ -Set B' }
if ($Prep) { exit (Invoke-Grader (@('--prep', '--set', $Set.ToUpper()) + $common)) }
if (-not $Submission) { throw 'ต้องระบุ -Submission (โฟลเดอร์ repo / ไฟล์ .bundle / โฟลเดอร์ที่มีหลาย .bundle กับ -All)' }

$targets = @()
if ($All) {
  $targets = @(Get-ChildItem -Path $Submission -Filter '*.bundle' | ForEach-Object { $_.FullName })
  if ($targets.Count -eq 0) { throw "ไม่พบ .bundle ใน $Submission" }
} else { $targets = @((Resolve-Path $Submission).Path) }

$rc = 0
foreach ($t in $targets) {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $a = @('--submission', $t, '--set', $Set.ToUpper(), '--e2e', $E2E) + $common
  if ($Variant -ge 0) { $a += @('--variant', "$Variant") }
  if ($Id -and -not $All) { $a += @('--id', $Id) }
  if ($Out -and -not $All) { $a += @('--out', $Out) }
  if ($Map) { $a += @('--map', $Map) }
  if ($Keep) { $a += '--keep' }
  $code = Invoke-Grader $a
  $sw.Stop()
  Write-Host ("== {0} → exit {1} · {2:N1} นาที" -f (Split-Path -Leaf $t), $code, $sw.Elapsed.TotalMinutes)
  if ($code -ne 0) { $rc = $code }
}
Write-Host "ผลรวมทุกคน: $(Join-Path $Work 'results\results.csv')"
exit $rc

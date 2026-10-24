<#
rea.ps1 — เรียก REA (image rea-lab:6.4.0) จาก PowerShell โดย mount โฟลเดอร์ปัจจุบันเป็น /work ใน container

กติกา: path ที่ส่งให้ REA ต้องเป็น path ใน container เสมอ (ขึ้นต้น /work/...) ไม่ใช่ C:\...

ตัวอย่าง (รันจากโฟลเดอร์บท 05):
  .\rea.ps1 doctor
  .\rea.ps1 -Out out\rea-static.json analyze-javascript-application /work/petshop/.next/static --json
  .\rea.ps1 -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --json
  .\rea.ps1 -Out out\scenario.json capture-browser-scenario /work/scenario-coupon.json --json
  .\rea.ps1 -Mcp          # MCP stdio server (ใช้กับ claude mcp add / --mcp-config)

ทำไมต้อง -Out: Windows PowerShell 5.1 ใช้ '>' แล้วได้ไฟล์ UTF-16 หรือ UTF-8 มี BOM
ซึ่ง REA ไม่รับเป็น JSON input ในคำสั่งถัดไป ("JSON input begins with a UTF-8 byte-order mark")
-Out ให้ container เขียนไฟล์เองจึงได้ UTF-8 ไม่มี BOM และภาษาไทยไม่เพี้ยน
#>
[CmdletBinding(PositionalBinding = $false)]  # กันไม่ให้ 'doctor' ถูกจับเป็นค่า -Out
param(
  [string]$Out,
  [string]$Network,
  [switch]$Mcp,
  [Parameter(ValueFromRemainingArguments = $true)][string[]]$ReaArgs
)
$image = 'rea-lab:6.4.0'
$work = (Get-Location).Path
$dockerArgs = @('run', '--rm', '-v', "${work}:/work", '-w', '/work')
if ($Network) { $dockerArgs += @('--network', $Network) }

if ($Mcp) {
  & docker @($dockerArgs + @('-i', $image, 'mcp'))
  exit $LASTEXITCODE
}

if ($Out) {
  $outPosix = '/work/' + ($Out -replace '\\', '/')
  # ไม่ฝัง " ใน argument เพราะ PowerShell 5.1 ส่ง quote ซ้อนให้โปรแกรมภายนอกไม่ถูก
  # จึงส่ง path ปลายทางเป็น env var และใช้ set -f; IFS= แทน "$@" (argument ที่มีช่องว่าง/ภาษาไทยยังอยู่ครบ)
  $dockerArgs += @('-e', "REA_OUT=$outPosix", '--entrypoint', 'sh', $image, '-c', 'set -f; IFS=; mkdir -p $(dirname $REA_OUT) && rea $@ > $REA_OUT', 'rea') + $ReaArgs
} else {
  $dockerArgs += @($image) + $ReaArgs
}
& docker @dockerArgs
exit $LASTEXITCODE

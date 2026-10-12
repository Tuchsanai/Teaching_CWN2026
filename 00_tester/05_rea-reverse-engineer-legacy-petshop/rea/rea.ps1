<#
rea.ps1 — เรียก REA (image rea-lab:6.4.0) จาก PowerShell โดย mount โฟลเดอร์ปัจจุบันเป็น /work ใน container

กติกา: path ที่ส่งให้ REA ต้องเป็น path ใน container เสมอ (ขึ้นต้น /work/...) ไม่ใช่ C:\...

ตัวอย่าง (รันจากรากบท 05 ใน PowerShell · ExecutionPolicy ค่าเริ่มต้นของ Windows 11 = Restricted จึงเรียกผ่าน -ExecutionPolicy Bypass):
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor --filter-output healthy,checks
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\v1-static.json analyze-javascript-application /work/out/v1/.next/static --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Mcp          # MCP stdio server

ทำไมต้อง -Out: Windows PowerShell 5.1 ใช้ '>' แล้วได้ไฟล์ UTF-16 หรือ UTF-8 มี BOM
ซึ่ง REA ไม่รับเป็น JSON input ในคำสั่งถัดไป ("JSON input begins with a UTF-8 byte-order mark")
-Out ให้ container เขียนไฟล์เองจึงได้ UTF-8 ไม่มี BOM และภาษาไทยไม่เพี้ยน

progress: REA เขียนบรรทัด JSON {"rea_progress":...} ลง stderr หลายร้อยบรรทัดต่อการ analyze (ท่วม context ของ agent)
สคริปต์นี้ทิ้งบรรทัด rea_progress ให้เอง (ข้อความ error อื่นใน stderr และ exit code ของ REA ยังอยู่ครบ) · อยากเห็น progress ใส่ -Progress
#>
[CmdletBinding(PositionalBinding = $false)]  # กันไม่ให้ 'doctor' ถูกจับเป็นค่า -Out
param(
  [string]$Out,
  [string]$Network,
  [switch]$Mcp,
  [switch]$Progress,
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

# ไม่ฝัง " ใน argument เพราะ PowerShell 5.1 ส่ง quote ซ้อนให้โปรแกรมภายนอกไม่ถูก
# จึงส่ง path ปลายทางเป็น env var และใช้ set -f; IFS= แทน "$@" (argument ที่มีช่องว่าง/ภาษาไทยยังอยู่ครบ)
# fd 3 = ปลายทางของ stdout (ไฟล์ -Out หรือหน้าจอ) · stderr ของ REA ผ่าน grep -v rea_progress · exit code เก็บใน /tmp/rc
$keep = if ($Progress) { '' } else { ' | grep --line-buffered -v rea_progress' }
$run = '{ rea $@ 2>&1 1>&3 3>&-; echo $? > /tmp/rc; }' + $keep + ' 1>&2; exit $(cat /tmp/rc)'
if ($Out) {
  $outPosix = '/work/' + ($Out -replace '\\', '/')
  $script = 'set -f; IFS=; mkdir -p $(dirname $REA_OUT) || exit 1; exec 3>$REA_OUT; ' + $run
  $dockerArgs += @('-e', "REA_OUT=$outPosix")
} else {
  $script = 'set -f; IFS=; exec 3>&1; ' + $run
}
$dockerArgs += @('--entrypoint', 'sh', $image, '-c', $script, 'rea') + $ReaArgs
& docker @dockerArgs
exit $LASTEXITCODE

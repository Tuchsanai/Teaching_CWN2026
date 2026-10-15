B=~/ai-accounts; S="vastai yolo cyolo"; L=/opt/local-skills
# copy local skill (-v มาที่ $L) เข้า shared ของ Claude + Codex
add() { [ -f "$1/SKILL.md" ] && [ "$2" != shared-check ] || { echo "SKIP $2"; return; }
  for t in .Claude .Codex; do rm -rf "${B:?}/${t:?}/shared/skills/${2:?}"; cp -rL "$1" "$B/$t/shared/skills/$2"; done
  echo "SYNCED $2"; S="$S $2"; }
if [ -f $L/SKILL.md ]; then add $L "$(basename "$(echo "$LOCAL_SKILLS_DIR" | tr '\' /)")"
else for d in $L/*/; do [ -d "$d" ] && add "$d" "$(basename "$d")"; done; fi
[ -d $L ] && [ "$S" = "vastai yolo cyolo" ] && echo "WARN LOCAL_SKILLS_DIR ไม่มี skill ที่มี SKILL.md"
# ตรวจ skill · docker ของ host (ให้ ssh ใช้ด้วย) · Vast key · บัญชีที่ล็อกอินแล้ว
for t in .Claude .Codex; do for s in $S; do [ -f $B/$t/shared/skills/$s/SKILL.md ] || echo "MISSING $t/$s"; done; done
grep -q ^DOCKER_HOST= /etc/environment || echo "DOCKER_HOST=$DOCKER_HOST" >> /etc/environment
echo "docker: $(docker info -f '{{.Name}}')"; vastai show user &>/dev/null && echo "VAST OK" || echo "VAST FAIL"
for i in 1 2 3 4 5; do
  CLAUDE_CONFIG_DIR=$B/.Claude/yolo$i claude auth status 2>/dev/null | grep -q '"loggedIn": true' && echo "LOGIN yolo$i"
  CODEX_HOME=$B/.Codex/cyolo$i codex login status 2>&1 | grep -q '^Logged in' && echo "LOGIN cyolo$i"
done; echo CHECKED

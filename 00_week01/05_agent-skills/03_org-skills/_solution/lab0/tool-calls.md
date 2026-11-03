# LAB 0 · คำสั่งที่ Claude รันจริง (จาก stream-json)

1. `Bash`
```bash
ls -la && cat compose.yml
```

2. `Bash`
```bash
cat .env.example .gitignore; ls seed people desks company-kit; docker ps -a --format '{{.Names}} {{.Status}}' | grep -i nova; docker info --format '{{.ServerVersion}}'
```

3. `Bash`
```bash
cp .env.example .env && docker compose up -d 2>&1 | tail -20
```

4. `Bash`
```bash
docker compose ps -a --format '{{.Service}} {{.State}} {{.ExitCode}}'; docker compose logs seed | tail -15; curl -s -u novatech-admin:novatech-admin-lab http://localhost:3300/api/v1/orgs | head -c 300; echo; curl -s -u novatech-admin:novatech-admin-lab "http://localhost:3300/api/v1/admin/users?limit=50" | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>JSON.parse(d).forEach(u=>console.log(u.login,"|",u.full_name)))'
```

5. `Bash`
```bash
curl -s -u novatech-admin:novatech-admin-lab "http://localhost:3300/api/v1/orgs/novatech/teams?limit=50" | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>JSON.parse(d).forEach(t=>console.log(t.name,"|",t.description)))'
```


เวลา 46.3 วินาที · 6 turns

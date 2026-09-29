# ==================================================================
# MultiAccount_Devtool — multiaccount_devtool:2569_1
#   ส่วนที่ 1 (บรรทัดนี้ถึง "ส่วนที่ 2"): ทุกอย่างของ base 00_Devtool_Container (devtools:2569_1)
#             เขียนซ้ำจาก ubuntu:24.04 ไม่ FROM image ของ base
#   ส่วนที่ 2: Claude Code, Codex CLI, wrapper yolo1..5 / cyolo1..5,
#             Playwright MCP + Chromium ส่วนกลาง, skill shared-check (สร้างตอน start ใน volume)
#   credential/config/session ไม่อยู่ใน image: /root/ai-accounts เป็น volume
# ==================================================================
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Bangkok \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        gnupg \
        lsb-release \
        software-properties-common \
        sudo \
        vim \
        nano \
        less \
        net-tools \
        iputils-ping \
        dnsutils \
        git \
        openssh-server \
        tzdata \
        python3 \
        python3-pip \
        python3-venv \
        python-is-python3 \
 && ln -fs "/usr/share/zoneinfo/${TZ}" /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# Git ล่าสุดจาก git-core PPA (git worktree ต้องใช้ git >= 2.5; Ubuntu 24.04 มี 2.43 อยู่แล้ว
# แต่ติดตั้งเวอร์ชันล่าสุดไว้เพื่อให้ได้ฟีเจอร์ worktree ครบทุกคำสั่ง เช่น repair/move)
RUN add-apt-repository -y ppa:git-core/ppa \
 && apt-get update && apt-get install -y --no-install-recommends git \
 && git --version \
 && git init -q /tmp/worktree-check \
 && git -C /tmp/worktree-check worktree list >/dev/null \
 && rm -rf /tmp/worktree-check /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# Node.js (LTS 22.x) สำหรับ run Next.js / React / Vite
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g npm@latest \
 && rm -rf /var/lib/apt/lists/*

RUN install -d /workspace

# ------------------------------------------------------------------
# JupyterLab + extensions (ติดตั้งลง system python เพื่อให้ kernel เห็น
# package เดียวกับที่ใช้ใน terminal / SSH)
#   - jupytext                : เปิด .py / .md เป็น notebook ได้ (pair notebook <-> script)
#   - jupyterlab-git          : Git UI ใน sidebar
#   - jupyterlab-lsp          : autocomplete / hover / diagnostics (python-lsp-server)
#   - jupyterlab-code-formatter + black + isort : จัดรูปแบบโค้ด
#   - jupyterlab-execute-time : แสดงเวลารันของแต่ละ cell
#   - jupyter-resource-usage  : แสดง CPU / RAM ใน status bar
#   - ipywidgets              : interactive widgets
#   - bash_kernel             : เขียน notebook ด้วย Bash kernel (เหมาะกับ DevTools lab)
# ------------------------------------------------------------------
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN pip install \
        "jupyterlab>=4.3,<5" \
        notebook \
        ipywidgets \
        jupytext \
        jupyterlab-git \
        jupyterlab-lsp \
        "python-lsp-server[all]" \
        jupyterlab-code-formatter \
        black \
        isort \
        jupyterlab-execute-time \
        jupyter-resource-usage \
        bash_kernel \
 && python -m bash_kernel.install --sys-prefix \
 && jupyter lab --version \
 && jupyter labextension list 2>&1 | grep -E 'enabled|OK' | head -20

# Jupyter Server config (system-wide)
RUN mkdir -p /etc/jupyter \
 && cat > /etc/jupyter/jupyter_server_config.py <<'EOF'
c = get_config()  # noqa

c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.root_dir = "/"          # เห็นทั้ง filesystem (โฟลเดอร์งานอยู่ที่ /workspace)
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.allow_remote_access = True

# แสดง hidden file / folder (ชื่อขึ้นต้นด้วย ".") ใน file browser เช่น .env .git .gitignore
# (ฝั่ง UI ตั้ง showHiddenFiles ไว้ใน overrides.json; ต้องเปิดทั้งสองฝั่งจึงจะเห็น)
c.ContentsManager.allow_hidden = True

# terminal ใน JupyterLab ใช้ bash login shell (อ่าน /etc/profile, ~/.bashrc)
c.ServerApp.terminals_enabled = True
c.ServerApp.terminado_settings = {"shell_command": ["/bin/bash", "-l"]}

# ไม่ใช้ token; รหัสผ่าน (ถ้ามี) ถูกตั้งจาก start.sh ผ่าน $JUPYTER_PASSWORD (default: ไม่มีรหัสผ่าน)
c.IdentityProvider.token = ""
c.PasswordIdentityProvider.allow_password_change = False
EOF

# JupyterLab UI defaults — file browser แสดง hidden file/folder และ terminal ให้ copy/paste ได้สะดวก:
#   * Ctrl+V           = paste (pasteWithCtrlV)
#   * Ctrl+Shift+C / V = copy / paste
#   * Ctrl+Insert / Shift+Insert = copy / paste
#   * คลิกขวาที่ terminal จะมีเมนู Copy / Paste
COPY jupyter_overrides.json /usr/local/share/jupyter/lab/settings/overrides.json

# ตั้งรหัสผ่าน root = passwd และเปิดให้ login ผ่าน SSH ได้ทั้ง password และ key
#   - password : ssh root@localhost -p 2223            (password: passwd)
#   - key      : ssh -i ssh/devtoolSSH root@localhost -p 2223
#     start.sh จะนำ public key จาก /etc/devtools/ssh/devtoolSSH.pub (mount มาจาก ./ssh บน host)
#     ไปใส่ใน /root/.ssh/authorized_keys ทุกครั้งที่ container start
RUN echo 'root:passwd' | chpasswd \
 && mkdir -p /etc/ssh/sshd_config.d /etc/devtools/ssh \
 && install -d -m 700 /root/.ssh \
 && printf 'PermitRootLogin yes\nPasswordAuthentication yes\nPubkeyAuthentication yes\n' \
      > /etc/ssh/sshd_config.d/10-root-login.conf


# ==================================================================
# ส่วนที่ 2 — ระบบหลายบัญชี (Claude Code + Codex CLI)
# ==================================================================
# เวอร์ชันปรับได้ด้วย --build-arg เช่น
#   docker build --build-arg CLAUDE_CODE_VERSION=latest --build-arg CODEX_VERSION=latest -t multiaccount_devtool:2569_1 .
# ถ้า npm ตอบ 404 เพราะเวอร์ชันเพิ่งออก (registry ยังไม่ sync) ลูปด้านล่างจะลองใหม่ 3 ครั้ง
# ถ้ายังไม่ได้ ให้ pin เวอร์ชันก่อนหน้า (npm view <pkg> versions)
ARG CLAUDE_CODE_VERSION=2.1.284
ARG CODEX_VERSION=0.159.0
ARG PLAYWRIGHT_MCP_VERSION=0.0.83

# Chromium ของ Playwright อยู่ใน image (นอก volume) ใช้ร่วมทุกบัญชี
# SSH session ไม่สืบทอด ENV นี้ — wrapper และ mcp.json ตั้งค่าให้เองจาก /etc/ai-accounts/ai-accounts.conf
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright

# npm 12 บล็อก install script เป็นค่าเริ่มต้น — Claude Code ต้องรัน postinstall (install.cjs) เพื่อวาง native binary
RUN for i in 1 2 3; do \
        npm install -g --no-fund --no-audit --allow-scripts=@anthropic-ai/claude-code \
            "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
            "@openai/codex@${CODEX_VERSION}" \
            "@playwright/mcp@${PLAYWRIGHT_MCP_VERSION}" && break; \
        echo "npm install failed (attempt $i) — retry in 20s"; sleep 20; \
    done \
 && claude --version && codex --version && playwright-mcp --version \
 && npm cache clean --force

# Chromium + system library ด้วย playwright ตัวที่อยู่ในแพ็กเกจ @playwright/mcp (เวอร์ชันตรงกัน)
# fonts-thai-tlwg: ให้ screenshot หน้าเว็บภาษาไทยไม่เป็นกล่องสี่เหลี่ยม
RUN cd "$(npm root -g)/@playwright/mcp" \
 && PW_CLI="$(node -e 'const p=require("path");console.log(p.join(p.dirname(require.resolve("playwright")),"cli.js"))')" \
 && node "$PW_CLI" install --with-deps chromium \
 && apt-get install -y --no-install-recommends fonts-thai-tlwg \
 && ls "$PLAYWRIGHT_BROWSERS_PATH" \
 && rm -rf /var/lib/apt/lists/*

# ระบบหลายบัญชี: config กลาง + wrapper + init + check
#   /usr/local/bin/ai-account          wrapper กลาง; yolo1..5 / cyolo1..5 เป็น symlink มาที่ไฟล์นี้ (อยู่ใน PATH ไม่ต้องแก้ .bashrc)
#   /usr/local/bin/ai-accounts-init    สร้างโฟลเดอร์บัญชี + shared ใน volume (start.sh เรียกทุกครั้ง, รันซ้ำได้)
#   /usr/local/bin/ai-accounts-check   ตรวจแบบไม่ต้องล็อกอิน พิมพ์ตาราง PASS/FAIL/SKIP
COPY scripts/ai-accounts.conf /etc/ai-accounts/ai-accounts.conf
COPY scripts/ai-account scripts/ai-accounts-init scripts/ai-accounts-check /usr/local/bin/
COPY scripts/mcp_json_to_codex.py scripts/mcp_stdio_probe.py /usr/local/lib/ai-accounts/
RUN chmod 755 /usr/local/bin/ai-account /usr/local/bin/ai-accounts-init /usr/local/bin/ai-accounts-check \
 && chmod 644 /etc/ai-accounts/ai-accounts.conf \
 && for n in 1 2 3 4 5; do \
        ln -sf ai-account "/usr/local/bin/yolo$n"; \
        ln -sf ai-account "/usr/local/bin/cyolo$n"; \
    done \
 && AI_ACCOUNTS_BASE=/tmp/ai-accounts-smoke ai-accounts-init >/dev/null \
 && AI_ACCOUNTS_BASE=/tmp/ai-accounts-smoke yolo1 --version \
 && AI_ACCOUNTS_BASE=/tmp/ai-accounts-smoke cyolo1 --version \
 && rm -rf /tmp/ai-accounts-smoke

# start script: sshd + dockerd + ai-accounts-init + jupyter lab (ไม่มีรหัสผ่าน เว้นแต่ตั้ง $JUPYTER_PASSWORD)
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

VOLUME /var/lib/docker
# credential/config/session ของทุกบัญชี + shared (skill, mcp.json) — ต้อง map เป็น named volume
VOLUME /root/ai-accounts

# 22=ssh, 8888=jupyterlab
EXPOSE 22 8888

WORKDIR /workspace

CMD ["/usr/local/bin/start.sh"]

# ==================================================================
# MultiAccountDevtool — tuchsanai/multi-account-devtool:2569_1
#   ส่วนที่ 1: สำเนา Dockerfile ของ 00_Devtool_Container (ทุกฟีเจอร์เดิม: SSH password/key,
#             Docker-in-Docker, Node 22, JupyterLab + extensions)
#   ส่วนที่ 2: Claude Code, Codex CLI, Playwright MCP + Chromium ส่วนกลาง,
#             installer หลายบัญชี ai-accounts-setup + wrapper yolo1..5 / cyolo1..5
#   credential/config/session ไม่อยู่ใน image — /root/ai-accounts เป็น named volume
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
#   - password : ssh root@localhost -p 2222            (password: passwd)
#   - key      : ssh -i ssh/devtoolSSH root@localhost -p 2222
#     start.sh จะนำ public key จาก /etc/devtools/ssh/devtoolSSH.pub (mount มาจาก ./ssh บน host)
#     ไปใส่ใน /root/.ssh/authorized_keys ทุกครั้งที่ container start
RUN echo 'root:passwd' | chpasswd \
 && mkdir -p /etc/ssh/sshd_config.d /etc/devtools/ssh \
 && install -d -m 700 /root/.ssh \
 && printf 'PermitRootLogin yes\nPasswordAuthentication yes\nPubkeyAuthentication yes\n' \
      > /etc/ssh/sshd_config.d/10-root-login.conf



# ==================================================================
# ส่วนที่ 2 — Claude Code + Codex CLI + Playwright MCP + ระบบหลายบัญชี
# ==================================================================
# ปรับเวอร์ชันได้ด้วย --build-arg เช่น --build-arg CLAUDE_CODE_VERSION=2.1.284
#   CLAUDE_CODE_VERSION : stable | latest | X.Y.Z  (ส่งให้ install.sh ทางการ)
#   CODEX_VERSION       : latest | X.Y.Z
#   PLAYWRIGHT_MCP_VERSION ต้อง pin เพื่อให้ Chromium ตรงกับ playwright ที่แพ็กเกจนี้ใช้
ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest
ARG PLAYWRIGHT_MCP_VERSION=0.0.83

# Claude Code — ตัวติดตั้งทางการ (native binary ลง /root/.local/bin/claude)
# ลิงก์เข้า /usr/local/bin เพื่อให้เรียก claude ได้จาก JupyterLab terminal, SSH และ docker exec
# โดยไม่ต้องแก้ .bashrc; ลบ downloads/สถานะที่ installer ทิ้งไว้ใน image (ไม่ให้มี state ติด image)
RUN curl -fsSL https://claude.ai/install.sh | bash -s "${CLAUDE_CODE_VERSION}" \
 && ln -sf /root/.local/bin/claude /usr/local/bin/claude \
 && rm -rf /root/.claude /root/.claude.json* \
 && claude --version

# Codex CLI (OpenAI) — npm global อยู่ใน /usr/bin (PATH ปกติอยู่แล้ว) ลิงก์ซ้ำไว้ใน /usr/local/bin ให้ชัด
RUN npm install -g --no-fund --no-audit "@openai/codex@${CODEX_VERSION}" \
 && ln -sf "$(npm prefix -g)/bin/codex" /usr/local/bin/codex \
 && codex --version \
 && npm cache clean --force

# Playwright MCP + Chromium ส่วนกลาง (ติดตั้งครั้งเดียวใน image นอก volume ใช้ร่วมทุกบัญชี)
# ใช้ playwright CLI ตัวที่อยู่ในแพ็กเกจ @playwright/mcp เอง → Chromium เวอร์ชันตรงกับ MCP
# fonts-thai-tlwg: screenshot หน้าเว็บภาษาไทยไม่เป็นกล่องสี่เหลี่ยม
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN npm install -g --no-fund --no-audit "@playwright/mcp@${PLAYWRIGHT_MCP_VERSION}" \
 && cd "$(npm root -g)/@playwright/mcp" \
 && PW_CLI="$(node -e 'const p=require("path");console.log(p.join(p.dirname(require.resolve("playwright")),"cli.js"))')" \
 && echo "playwright CLI: $PW_CLI ($(node "$PW_CLI" --version))" \
 && node "$PW_CLI" install --with-deps chromium \
 && apt-get install -y --no-install-recommends fonts-thai-tlwg \
 && ls "$PLAYWRIGHT_BROWSERS_PATH" \
 && playwright-mcp --version \
 && npm cache clean --force \
 && rm -rf /var/lib/apt/lists/*

# ระบบหลายบัญชี
#   /etc/ai-accounts.conf              BASE_PATH="$HOME/ai-accounts" (แก้ที่นี่ที่เดียว) + รายชื่อบัญชี
#   /usr/local/bin/ai-accounts-setup   installer (รันซ้ำได้) — start.sh เรียกทุกครั้งที่ container start
#   /usr/local/bin/ai-account          wrapper กลาง; yolo1..5 / cyolo1..5 เป็น symlink มาที่ไฟล์นี้
#   /usr/local/lib/ai-accounts/        ตัวช่วย: แปลง mcp.json → -c ของ Codex, ทดสอบ MCP ผ่าน stdio
COPY scripts/ai-accounts.conf /etc/ai-accounts.conf
COPY scripts/ai-accounts-setup scripts/ai-account /usr/local/bin/
COPY scripts/mcp_json_to_codex.py scripts/mcp_stdio_probe.py /usr/local/lib/ai-accounts/
RUN chmod 755 /usr/local/bin/ai-accounts-setup /usr/local/bin/ai-account /usr/local/lib/ai-accounts/*.py \
 && for n in 1 2 3 4 5; do \
        ln -sf ai-account "/usr/local/bin/yolo$n"; \
        ln -sf ai-account "/usr/local/bin/cyolo$n"; \
    done \
 && HOME=/tmp/ai-smoke ai-accounts-setup >/dev/null \
 && HOME=/tmp/ai-smoke yolo1 --version \
 && HOME=/tmp/ai-smoke cyolo1 --version \
 && rm -rf /tmp/ai-smoke

# start script: sshd + dockerd + ai-accounts-setup + jupyter lab
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

VOLUME /var/lib/docker
# credential/config/session ของทุกบัญชี + shared (skills, mcp.json) — map เป็น named volume
VOLUME /root/ai-accounts

# 22=ssh, 8888=jupyterlab
EXPOSE 22 8888

WORKDIR /workspace

CMD ["/usr/local/bin/start.sh"]

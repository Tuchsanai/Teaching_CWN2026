# Authoring-environment note (devtools side effect)

While authoring LAB 004 on 2026-09-24, yolo3 ran `playwright install --with-deps chromium` inside the
`devtools` container for a local headless UI check that was later dropped from scope. The `--with-deps`
step installed system libraries with apt. This note records exactly what `/var/log/apt/history.log` shows
for that single transaction (other apt history is not reproduced here).

| Field | Value |
|---|---|
| Start / end | 2026-09-24 17:20:26 → 17:20:38 (container local time) |
| Command | `apt-get install -y --no-install-recommends <Chromium runtime libraries>` (run by Playwright) |
| Newly installed | 93 packages (31 requested by Playwright, 62 pulled in automatically) |
| Upgraded / downgraded / removed / purged | none (no such lines in this transaction) |

## What was cleaned up and what was not

- Removed afterwards: the `playwright` Python package in the temporary venv `/tmp/lab04venv` and the downloaded browser in `/root/.cache/ms-playwright`.
- Still present (temporary, outside the lab folder): `/tmp/lab04venv` with the pinned FastAPI test dependencies used for the unit tests.
- **Not removed: the apt packages below.** They were left in place on purpose, because removing shared libraries could break other work in devtools. They can be removed later with apt after checking nothing else depends on them.
- devtools was **not** rebuilt or recreated, the Docker socket was not mounted, and the account wrappers (`yolo*`, `cyolo*`) and credentials in `~/ai-accounts` were not modified. Apart from that temporary venv in `/tmp`, the apt packages listed here are the only system-level change from the authoring step.

## Requested by Playwright (31)

| Package | Version |
|---|---|
| `xfonts-cyrillic:amd64` | 1:1.0.5+nmu1 |
| `fonts-wqy-zenhei:amd64` | 0.9.45-8 |
| `libpango-1.0-0:amd64` | 1.52.1+ds-1build1 |
| `libcairo2:amd64` | 1.18.0-3build1 |
| `libgbm1:amd64` | 25.2.8-0ubuntu0.24.04.2 |
| `libfreetype6:amd64` | 2.13.2+dfsg-1ubuntu0.1 |
| `libxcb1:amd64` | 1.15-1ubuntu2 |
| `libxcomposite1:amd64` | 1:0.4.5-1build3 |
| `libxdamage1:amd64` | 1:1.1.6-1build1 |
| `libfontconfig1:amd64` | 2.15.0-1.1ubuntu2 |
| `libcups2t64:amd64` | 2.4.7-1.2ubuntu7.14 |
| `libatspi2.0-0t64:amd64` | 2.52.0-1build1 |
| `libasound2t64:amd64` | 1.2.11-1ubuntu0.3 |
| `libxrandr2:amd64` | 2:1.5.2-2build1 |
| `libxkbcommon0:amd64` | 1.6.0-1build1 |
| `libnss3:amd64` | 2:3.98-1ubuntu0.2 |
| `fonts-liberation:amd64` | 1:2.1.5-3 |
| `libatk1.0-0t64:amd64` | 2.52.0-1build1 |
| `xvfb:amd64` | 2:21.1.12-1ubuntu1.8 |
| `fonts-noto-color-emoji:amd64` | 2.047-0ubuntu0.24.04.1 |
| `libdrm2:amd64` | 2.4.125-1ubuntu0.1~24.04.2 |
| `libxext6:amd64` | 2:1.3.4-1build2 |
| `fonts-freefont-ttf:amd64` | 20211204+svn4273-2 |
| `fonts-tlwg-loma-otf:amd64` | 1:0.7.3-1 |
| `xfonts-scalable:amd64` | 1:1.0.3-1.3 |
| `libx11-6:amd64` | 2:1.8.7-1build1 |
| `fonts-unifont:amd64` | 1:15.1.01-1build1 |
| `libatk-bridge2.0-0t64:amd64` | 2.52.0-1build1 |
| `fonts-ipafont-gothic:amd64` | 00303-21ubuntu1 |
| `libxfixes3:amd64` | 1:6.0.0-2build1 |
| `libnspr4:amd64` | 2:4.35-1.1build1 |

## Installed automatically as dependencies (62)

| Package | Version |
|---|---|
| `fontconfig:amd64` | 2.15.0-1.1ubuntu2 |
| `libvulkan1:amd64` | 1.3.275.0-1build1 |
| `libxcb-present0:amd64` | 1.15-1ubuntu2 |
| `libxxf86vm1:amd64` | 1:1.1.4-1build4 |
| `libglx-mesa0:amd64` | 25.2.8-0ubuntu0.24.04.2 |
| `libdatrie1:amd64` | 0.2.13-3build1 |
| `libthai0:amd64` | 0.1.29-2build1 |
| `xkb-data:amd64` | 2.41-2ubuntu1.1 |
| `libxrender1:amd64` | 1:0.9.10-1.1build1 |
| `libglvnd0:amd64` | 1.7.0-1build1 |
| `libsensors-config:amd64` | 1:3.6.0-9build1 |
| `libx11-xcb1:amd64` | 2:1.8.7-1build1 |
| `libxshmfence1:amd64` | 1.3-1build5 |
| `libxkbfile1:amd64` | 1:1.1.0-1build4 |
| `libavahi-common-data:amd64` | 0.8-13ubuntu6.2 |
| `libxcb-dri3-0:amd64` | 1.15-1ubuntu2 |
| `libpciaccess0:amd64` | 0.17-3ubuntu0.24.04.3 |
| `libxmuu1:amd64` | 2:1.1.3-3build2 |
| `x11-common:amd64` | 1:7.7+23ubuntu3 |
| `libglx0:amd64` | 1.7.0-1build1 |
| `libfribidi0:amd64` | 1.0.13-3build1 |
| `mesa-libgallium:amd64` | 25.2.8-0ubuntu0.24.04.2 |
| `libpixman-1-0:amd64` | 0.42.2-1build1 |
| `libxau6:amd64` | 1:1.0.9-1build6 |
| `libxaw7:amd64` | 2:1.0.14-1build2 |
| `libllvm20:amd64` | 1:20.1.2-0ubuntu1~24.04.3 |
| `libxmu6:amd64` | 2:1.1.3-3build2 |
| `libgraphite2-3:amd64` | 1.3.14-2ubuntu0.24.04.1 |
| `libxpm4:amd64` | 1:3.5.17-1ubuntu0.24.04.1 |
| `libgl1-mesa-dri:amd64` | 25.2.8-0ubuntu0.24.04.2 |
| `libxfont2:amd64` | 1:2.0.6-1+deb13u1build0.24.04.2 |
| `libfontenc1:amd64` | 1:1.1.8-1build1 |
| `fontconfig-config:amd64` | 2.15.0-1.1ubuntu2 |
| `libdrm-common:amd64` | 2.4.125-1ubuntu0.1~24.04.2 |
| `libx11-data:amd64` | 2:1.8.7-1build1 |
| `libxt6t64:amd64` | 1:1.2.1-1.2build1 |
| `xauth:amd64` | 1:1.1.2-1build1 |
| `libxcb-render0:amd64` | 1.15-1ubuntu2 |
| `xserver-common:amd64` | 2:21.1.12-1ubuntu1.8 |
| `libice6:amd64` | 2:1.0.10-1build3 |
| `xfonts-encodings:amd64` | 1:1.0.5-0ubuntu2 |
| `x11-xkb-utils:amd64` | 7.7+8build2 |
| `libasound2-data:amd64` | 1.2.11-1ubuntu0.3 |
| `libthai-data:amd64` | 0.1.29-2build1 |
| `libavahi-common3:amd64` | 0.8-13ubuntu6.2 |
| `libxcb-glx0:amd64` | 1.15-1ubuntu2 |
| `xfonts-utils:amd64` | 1:7.7+6build3 |
| `libdrm-amdgpu1:amd64` | 2.4.125-1ubuntu0.1~24.04.2 |
| `libsensors5:amd64` | 1:3.6.0-9build1 |
| `libxcb-randr0:amd64` | 1.15-1ubuntu2 |
| `libharfbuzz0b:amd64` | 8.3.0-2build2 |
| `libxcb-shm0:amd64` | 1.15-1ubuntu2 |
| `libgl1:amd64` | 1.7.0-1build1 |
| `libpng16-16t64:amd64` | 1.6.43-5ubuntu0.6 |
| `libxcb-sync1:amd64` | 1.15-1ubuntu2 |
| `at-spi2-common:amd64` | 2.52.0-1build1 |
| `libavahi-client3:amd64` | 0.8-13ubuntu6.2 |
| `libsm6:amd64` | 2:1.2.3-1build3 |
| `libdrm-intel1:amd64` | 2.4.125-1ubuntu0.1~24.04.2 |
| `libxdmcp6:amd64` | 1:1.1.3-0ubuntu6 |
| `libxi6:amd64` | 2:1.8.1-1build1 |
| `libxcb-xfixes0:amd64` | 1.15-1ubuntu2 |

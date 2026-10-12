# rea-lab: REA (Reverse Engineer Anything) แบบรันใน container
# ทำไมต้อง container: REA ทดสอบจริงบน Linux และเป็นโค้ดภายนอก แยกไว้ใน container ปลอดภัยกว่า
# base = Playwright 1.63 (มี Chromium ให้ฟีเจอร์ฝั่งเบราว์เซอร์ของ REA) + procps (REA ต้องใช้ ps)
FROM mcr.microsoft.com/playwright:v1.63.0-noble
RUN apt-get update && apt-get install -y --no-install-recommends procps jq && rm -rf /var/lib/apt/lists/*
RUN npm install -g rea-agents@6.4.0 && rea --help >/dev/null
ENV REA_BROWSER_EXECUTABLE=/ms-playwright/chromium-1243/chrome-linux64/chrome
WORKDIR /work
ENTRYPOINT ["rea"]

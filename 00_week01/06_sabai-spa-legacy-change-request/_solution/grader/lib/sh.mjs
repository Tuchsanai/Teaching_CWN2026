// รันคำสั่งภายนอก (docker / git / tar) แบบไม่ผ่าน shell · มี timeout
import { spawn } from "node:child_process";

export function sh(cmd, args, o = {}) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    let out = "", err = "";
    let p;
    try {
      p = spawn(cmd, args, { cwd: o.cwd, env: { ...process.env, ...(o.env ?? {}) }, windowsHide: true });
    } catch (e) {
      resolve({ code: 127, out: "", err: String(e), ms: 0 });
      return;
    }
    p.stdout.setEncoding("utf8");
    p.stderr.setEncoding("utf8");
    p.stdout.on("data", (d) => { out += d; if (out.length > 8e6) out = out.slice(-6e6); o.onOut?.(d); });
    p.stderr.on("data", (d) => { err += d; if (err.length > 4e6) err = err.slice(-3e6); });
    if (o.input !== undefined) p.stdin.end(o.input);
    else p.stdin.end();
    let timedOut = false;
    const timer = o.timeoutMs
      ? setTimeout(() => {
          timedOut = true;
          if (o.killName) spawn("docker", ["rm", "-f", o.killName], { windowsHide: true });
          setTimeout(() => p.kill(), 2000);
        }, o.timeoutMs)
      : null;
    p.on("error", (e) => { err += String(e); });
    p.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({ code: timedOut ? 124 : code ?? 1, out, err, ms: Date.now() - t0, timedOut });
    });
  });
}
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

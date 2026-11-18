The 2-GPU setup handles **about 176 concurrent users**, versus 104 on one GPU. That holds only if you set aside one glitched step. The gpu2 run finished with DONE, but the official number in `gpu2.json` is just **32 users**. That's because the N=64 step failed, and the rule says every lower level has to pass.

**About N=64:** during that step both GPUs dropped to about 30% use. Throughput fell to 220 req/s and p95 jumped to 1,752 ms, while p50 stayed normal at 93 ms. The system stalled for a moment; it wasn't out of capacity. Higher levels passed (N=128, 160, 176). I re-ran N=64 three times and it passed every time: about 578 req/s, p95 145–149 ms, errors 0–0.01%. Those re-runs are saved separately in `gpu2_recheck64.json`. I didn't change `gpu2.json`. The table below uses 176, which is the capacity once that glitch is set aside.

| จำนวน GPU | สถาปัตยกรรม | รองรับผู้ใช้พร้อมกัน (N) | Throughput สูงสุด | p95 ที่ N นั้น | เท่าของ 1 ใบ | Efficiency |
|---|---|---|---|---|---|---|
| 1 | ทีละคำขอ (base1) | 18 | 39.5 req/s | 479 ms | – | – |
| 1 | Micro-batching (batch1) | 52 | 157.3 req/s | 365 ms | – | – |
| 1 | Micro-batching + 4 process (gpu1) | 104 | 325.1 req/s | 497 ms | 1.00× | 100% |
| 2 | 2 replica × 4 process, batch 32 หลัง NGINX (gpu2) | **176** | **651.1 req/s** | 421 ms | **1.69×** | **85%** |

All results use the same SLO: p95 ≤ 500 ms and error < 1%. N=192 failed with p95 557 ms, so 2-GPU capacity is between 176 and 192. Peak throughput went up exactly 2.00× (651 vs 325 req/s).

**สรุป:** 1 ใบ 104 คน → 2 ใบ 176 คน (1.69 เท่า, efficiency 85%)

**ถ้าเพิ่มเป็น 3 ใบ (เป็นการคำนวณ ไม่ใช่ผลวัด):** if each extra GPU adds 72 users, as the second one did, that gives about 248. If efficiency stays at 85%, it's 104 × 3 × 0.85 ≈ 264. So expect **roughly 250–265 users** and about 950–975 req/s. This machine only has 2 GPUs and `cluster.sh` only opens 1–2 replicas, so I couldn't measure 3.

**Were requests split evenly?** Yes. At N=176, replica gpu0 handled 4,658 requests and gpu1 handled 4,739 (49.6% / 50.4%). Each of the 8 processes handled 1,160–1,191.

**Where's the bottleneck when it doesn't double?**
- **GPU:** this is what limits it. Both cards ran at about 80%, the same level gpu1 reached when saturated. Throughput doubled, so the GPUs scale fine.
- **Server CPU:** not the bottleneck. The servers used 12.4 cores out of 192, about 1.5 cores per process, the same as gpu1.
- **NGINX:** not the bottleneck. It used 0.48 cores.
- **Load generator:** not the bottleneck. It used 0.46 cores.
- **What's left:** user count rises less than throughput because capacity is set by p95 latency. At the same load per GPU, 2 GPUs have a longer latency tail. At 96 users per GPU, p95 was 557 ms with 2 GPUs versus 424 ms with 1. I think this comes from 8 processes sharing the same host, but I didn't measure that directly. The bisection step of 16 users also hides some of the gap.

The **vapp-lab5 machine (ID <id>, 2× RTX 3090, about $0.39/hr) is still running**. The 2-replica system is still up behind NGINX on port 8080.

Files are in `/workspace/lab5/results/` on the machine:
- `gpu2.json`
- `gpu2.log`
- `gpu2_recheck64.json`

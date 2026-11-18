The Worker-kill test passed: all 89 good jobs finished and none were lost. The report produced `metrics.json` and 6 charts, all copied back to your folder. The machine **vapp-lab9 is still running.**

## Worker kill test (2 Workers, 90 jobs in 2.97 s, gpu1 killed at second 4.0)

| Item | Result |
|---|---|
| Good jobs sent | **89** (all 90 jobs were accepted) |
| Good jobs finished | **89/89, 0 lost.** All 89 images downloaded and are valid JPEGs |
| Redelivered | **4.** gpu1 was drawing 4 images when it was killed; all 4 went back to the queue and gpu0 finished them |
| Bad job → Dead-letter queue | **1** |
| Who finished what | gpu0: 76 jobs · gpu1: 13 (before it was killed) |
| Timing | All jobs done at 20.2 s · gpu1 restarted at 21.4 s, ready again at 31.3 s · now 2 Workers |

The gateway rejects a truly empty message (zero characters), so the bad job was sent as spaces only. The Worker reads it as an empty message and rejects it.

## 1 / 2 GPU table

| GPUs | Architecture | Max concurrent users (N) | Max images/s | p95 at that N | × Baseline (1 GPU) | Efficiency vs hybrid 1 GPU |
|---|---|---|---|---|---|---|
| 1 | Synchronous (Baseline) | 30 | 2.15 | 9.19 s | 1.00× | – |
| 1 | Hybrid, 1 Worker | 52 | 3.8 | 9.57 s | 1.73× | 100% |
| 2 | Hybrid, 2 Workers | 104 | 7.4 | 9.63 s | 3.47× | users 100% · img/s 97% |
| 3 | Hybrid (**estimated**, not measured) | ~156 | ~11.1 | – | – | – |

The 3-GPU row is the 1-GPU figure × 3 × the efficiency measured at 2 GPUs. The 7.4 images/s for 2 GPUs was measured at N = 128, which is already past the SLO.

## Charts (`lab9_hybrid/results/`)
1. `1_latency_vs_users.png`: p50 and p95 wait vs N for all 3 systems, with the SLO line at 10 s and capacity stars
2. `2_throughput_vs_users.png`: images per second vs N
3. `3_scaling_vs_gpus.png`: capacity and max images per second vs number of GPUs, with the ideal line and the 3-GPU point labelled "estimated"
4. `4_burst_sync_vs_hybrid.png`: jobs pending over time during the burst
   - Synchronous: 71 of 200 users got their image; 129 images were drawn for nobody
   - Hybrid: 200 of 200 users got their image; 0 wasted
5. `5_express_vs_normal.png`: express p95 2.1 s vs normal 43.4 s
6. `6_kill_worker_timeline.png`: job counts over time, with the kill, restart and gpu1-back times marked

## Files
- **Code:** new `code/killtest.py` (the kill test) and `code/report.py`. I also copied every file from `code/` and the full results set into `lab9_hybrid/` in your current folder.
- **`code/web/.env`:** 2 lines, with `T2I_BASE_URL` set to the gateway's external address (`http://203.0.113.10:41234`). From this machine the gateway answers 200 with the key and 401 without it. The key was never displayed.

**The machine vapp-lab9 is still running.** RabbitMQ, the gateway on port 8000 and both Workers (gpu0, gpu1) are up, ready for step 10.

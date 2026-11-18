The run finished and the machine is deleted: one GPU handling one request at a time held **28 users**, and two GPUs with micro-batching plus 4 processes held **192 users**. Nothing is left running in the Vast.ai account, and the whole run cost **$0.097**.

**Machine**
- 2× RTX 3090 in California, US, at $0.395/hr including disk, under the $0.60 cap. It's the same machine type as the main run.
- The container got about 26.3 CPU cores.
- It took 30 s from renting to working SSH, and the install took 128 s.

**API test:** every sample image returned 200 with detected objects. The model took about 20–68 ms per image. A request with no key or a wrong key got 401.

## Capacity table (target: p95 ≤ 500 ms and error < 1%)

| Setup | Capacity this run | Max throughput | p95 at capacity | Main run (`results`) |
|---|---|---|---|---|
| 1 GPU, one request at a time (`base1`) | **28 users** | 61 req/s | 484 ms | 22 users · 63 req/s |
| 2 GPUs, micro-batching + 4 processes (`gpu2`) | **192 users** | 660 req/s (640 at capacity) | 452 ms | 176 users · 651 req/s (strict 32) |
| How many times larger | **6.9×** | 10.8× | | 8.0× |

In the main run, `gpu2` had a one-off p95 spike at N=64 (that is why its strict capacity was 32). That did not happen this time: the strict capacity also came out at 192.

## Each level
**`base1`**
| N | Throughput | p50 / p95 / p99 (ms) | GPU util | Pass? |
|---|---|---|---|---|
| 16 | 58 req/s | 274 / 313 / 350 | 18% | pass |
| 64 | 56 req/s | 1115 / 1374 / 1467 | 17% | fail |
| 128 | 60 req/s | 2130 / 2259 / 2283 | 19% | fail |
| 28 (bisected) | 61 req/s | 457 / 484 / 506 | 19% | pass |
| 34 (bisected) | 50 req/s | 740 / 772 / 781 | 15% | fail |
| 40 (bisected) | 61 req/s | 650 / 729 / 834 | 19% | fail |

**`gpu2`**
| N | Throughput | p50 / p95 / p99 (ms) | GPU0 / GPU1 util | Avg batch | Pass? |
|---|---|---|---|---|---|
| 16 | 308 req/s | 52 / 68 / 78 | 80% / 79% | 1.2 | pass |
| 64 | 578 req/s | 110 / 150 / 182 | 80% / 80% | 4.5 | pass |
| 128 | 624 req/s | 186 / 379 / 662 | 79% / 80% | 9.3 | pass |
| 192 (bisected) | 640 req/s | 288 / 452 / 562 | 81% / 77% | 13.7 | pass |
| 208 (bisected) | 625 req/s | 314 / 532 / 605 | 82% / 76% | 15.1 | fail |
| 224 (bisected) | 621 req/s | 317 / 592 / 775 | 78% / 82% | 16.2 | fail |
| 256 | 633 req/s | 380 / 681 / 918 | 87% / 74% | 18.1 | fail |
| 512 | 661 req/s | 792 / 1216 / 1439 | 84% / 82% | 28.8 | fail |

Error was 0% at every level in both setups.

**GPU 1 card, one request at a time: 28 users → 2 cards with micro-batching + 4 processes: 192 users (6.9×)**

- **Bottleneck for one request at a time:** throughput stays flat at about 60 req/s whatever N is, while the GPU sits at only about 18%. The cause is that the model is called one image at a time. Extra users just wait in the queue.
- **Bottleneck for 2 GPUs:** each GPU stays at about 80%, and the server processes use about 12.4 CPU cores. Above N≈192, throughput stays around 625–660 req/s and the extra users only add queueing time.
- **This 6.9× mixes two effects:** the change in setup and the second GPU. I didn't run `gpu1` (1 GPU with micro-batching + 4 processes), so the two can't be separated. That is also why there's no 3-GPU estimate and no scaling chart.

**Why `base1` came out at 28 instead of the reference 22:** you asked for coarser levels, so the bisection checked N=28, 34 and 40 rather than 20, 22 and 24. Throughput was about the same in both runs (61 vs 63 req/s), so the true limit is about 28–30 users either way.

## Times and actual cost
| Step | Time |
|---|---|
| Rent until SSH works | 0.5 min |
| Copy files, install, test API | 4.8 min |
| `base1` | 2.6 min |
| Start 8 processes + `gpu2` | 5.7 min |
| Pull results + delete machine | 0.6 min |
| **Machine up in total** | **14.4 min (0.233 hr)** |

Invoice: GPU $0.081 + disk $0.011 + download $0.005 = **$0.097**. The main run cost $1.011.

## Checks
- ✅ 2× RTX 3090 at $0.395/hr, with about 26.3 CPU cores (24 or more required).
- ✅ The install log ends with `DONE`, and the API test passed as above.
- ✅ Both sets have their `.json` result with a capacity number, and both logs end with `DONE`.
- ✅ Error was 0% everywhere.
- ✅ The load generator and NGINX each used under 0.5 core, so neither was the bottleneck.
- ✅ Requests were spread evenly across the two GPUs (within about 2%).
- ✅ No API key value appears in any result file, and the main `results` folder was not overwritten.
- ✅ The machine is deleted and none remain in the account.


In `latency_p95_vs_users.png`, the "SLO p95 = 500 ms" label sits far to the left of the plot and leaves empty space. That comes from `report.py`; the numbers are correct.


Files are in `lab5_image_api/results_skill/`:
- `base1.json`
- `gpu2.json`
- `metrics.json`
- `latency_p95_vs_users.png`
- `throughput_vs_users.png`
- `dataset_samples.jpg`
- `test_single.json`
- logs, `install_time.txt`, `cluster.conf`

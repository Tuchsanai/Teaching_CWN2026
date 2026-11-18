I wrote `lab5_cluster_vlm/code/report.py` and ran it. It reads the raw results from steps 3–7 and writes `results/metrics.json` plus 4 graphs in `results/images/`. The speedups it computes match the step 5 table exactly.

## LAB 5 summary (measured, RTX 3090 × 2 per Node)

| แนวทาง | จำนวน Node | จำนวน GPU | replica | Effective Batch | วินาทีต่อการปรับน้ำหนัก 1 ครั้ง (คำนวณ / สื่อสาร) | ใบเสร็จต่อวินาที | Speedup | Efficiency | ราคาต่อชั่วโมง | เงินต่อ Epoch (800 ใบ) |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 1 | 2 | 1 | 8 | 9.19 (9.14 / 0.04) | 0.870 | 1.00× | 100% | $0.414 | $0.106 (15.3 นาที) |
| A | 2 | 4 | 2 | 8 | 7.29 (4.28 / 3.00) | 1.097 | 1.26× | 63% | $0.924 | $0.187 (12.2 นาที) |
| A | 1 | 2 | 1 | 32 | 35.91 (35.86 / 0.04) | 0.891 | 1.00× | 100% | $0.414 | $0.103 (15.0 นาที) |
| A | 2 | 4 | 2 | 32 | 19.32 (17.17 / 2.13) | 1.656 | **1.86×** | **93%** | $0.924 | $0.124 (8.0 นาที) |
| B | 1 | 2 | 2 | 8 | 5.29 (4.91 / 0.36) | 1.513 | 1.00× | 100% | $0.414 | $0.061 (8.8 นาที) |
| B | 2 | 4 | 4 | 8 | 4.65 (2.36 / 2.27) | 1.722 | 1.14× | 57% | $0.924 | $0.119 (7.7 นาที) |
| B | 1 | 2 | 2 | 32 | 20.03 (19.32 / 0.70) | 1.598 | 1.00× | 100% | $0.414 | **$0.058** (8.3 นาที) |
| B | 2 | 4 | 4 | 32 | 11.11 (9.47 / 1.62) | **2.880** | 1.80× | 90% | $0.924 | $0.071 (**4.6 นาที**) |

- **Checksums:** every replica's checksum matches in all 8 runs, and in both training rounds of step 6.
- **Gradient size:** 7.67 MB per replica per update, which is 3,833,856 LoRA parameters in bf16.
- **Network between the nodes:** RTT 55.5 ms. Sending 7.6 MB and receiving it back took about 0.33 s.
- **The first B · EB 32 · 2 Node run** hit a network stall and got only 1.14×. It is recorded separately in `runs_excluded` and is not used in the table.

## 3-Node estimate (calculated from measured times, not a measurement)

**How I calculated it:** compute time per receipt on Node 1 × the number of receipts on the slowest replica, plus the overhead measured at 2 Node.
- **Optimistic case:** the overhead stays the same as at 2 Node.
- **Pessimistic case:** the overhead doubles, because 2 remote nodes share the link into the coordinator.
- **Uneven split:** neither 8 nor 32 divides evenly over 3 or 6 replicas, so the slowest replica gets more receipts than the others.

| กรณี | replica | ใบเสร็จบน replica ที่ช้าสุด | Speedup โดยประมาณ | Efficiency |
|---|---|---|---|---|
| A · EB 8 | 3 | 3 | 1.04–1.49× | 35–50% |
| A · EB 32 | 3 | 11 | 2.38–2.62× | 79–87% |
| B · EB 8 | 6 | 2 | 0.77–1.14× (might even get slower) | 26–38% |
| B · EB 32 | 6 | 6 | 1.97–2.30× | 66–77% |

## The 4 questions

**1. How much faster with more Nodes?** Going from 1 to 2 Nodes gave between 1.14× and 1.86×:
- **Effective Batch 32:** A 1.86× and B 1.80×.
- **Effective Batch 8:** A 1.26× and B 1.14×.
- **Fastest overall:** B · EB 32 · 2 Node, at 2.88 receipts per second, or 4.6 minutes per Epoch.
- **Cost:** money per Epoch went up in every case, because 2 Nodes cost $0.924/h, which is 2.23 times the price of 1 Node. The best gain in speed was only 1.86×.

**2. Why doesn't it speed up in line with the number of Nodes?** Every update has to send the gradient across countries (Quebec ↔ Utah) and wait for every replica before it can continue.
- **Communication:** it rose from 0.04 s on 1 Node to 3.00 s (A · EB 8) and from 0.36 s to 2.27 s (B · EB 8).
- **Most of that is waiting:** the replica that finishes first waits for the slowest one. The coordinator also sends the average back to the remote node, which takes about 0.5 s in B · EB 8 and about 0.6 s in A · EB 8.
- **The fixed cost:** the 55.5 ms RTT and about 0.33 s per 7.6 MB are paid on every update, however few receipts it covers.

**3. Why does Effective Batch 32 get a different Efficiency from 8?** The gradient is always 7.67 MB, so communication costs about 1.6–3 s per update either way. Compute time, though, grows with the number of receipts per update.

| | Compute per update (2 Node) | Share of time spent communicating | Efficiency |
|---|---|---|---|
| A · EB 8 | 4.28 s | 41% | 63% |
| A · EB 32 | 17.17 s | 11% | 93% |
| B · EB 8 | 2.36 s | 49% | 57% |
| B · EB 32 | 9.47 s | 15% | 90% |

With EB 32 the same communication cost is spread over 4 times as many receipts. The trade-off is fewer weight updates per Epoch.

**4. When to use A and when to use B**

**Use B when the model fits on one GPU at batch 1 with Gradient Checkpointing on:**
- **Peak VRAM:** 20.4 GiB per card.
- **Faster on the same machine:** 1.51–1.60 receipts per second, against 0.87–0.89 for A. That is about 1.7× faster, because A's GPUs take turns (utilization around 50%).
- **Cheapest per Epoch:** $0.058 at 1 Node · EB 32.
- **Same quality as A:** final loss 0.0426 for both, Item F1 87.2 for B against 87.9 for A.
- **Little VRAM to spare:** only about 3.3 GiB is left, and batch 2 runs out of memory.

**Use A when one GPU can't hold the model:**
- **One GPU without Gradient Checkpointing:** out of memory at 23.0 GiB.
- **A's headroom:** it uses only 15.3 GiB per card, leaving about 8 GiB. That suits longer receipts, larger images, or setups where Gradient Checkpointing can't be used.

**When to add a Node:** only when you need the job finished sooner and can use a large Effective Batch (32 or more). With EB 8, adding a Node costs more and is barely faster.

Files are in `lab5_cluster_vlm/`:
- `code/report.py`
- `results/metrics.json`
- `results/images/`:
  - `speedup_vs_nodes.png`
  - `time_per_update.png`
  - `peak_vram.png`
  - `cost_per_epoch.png`

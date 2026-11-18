I trained both rounds on the 2-node cluster, A first and then B. Every replica in each round ended with the same LoRA checksum. One LoRA adapter per round is saved at `results/adapter_A` and `results/adapter_B`. Each round used the first 400 receipts of the Training Set (shuffled with seed 0), 1 Epoch, Effective Batch 8, which gave 50 weight updates. Round B started over from the base model: every replica was a new process that loaded the model again.

| | แนวทาง A | แนวทาง B |
|---|---|---|
| replica | 2 (Node ละ 1 ตัว · โมเดลแบ่งบน GPU 2 ใบ) · สะสมตัวละ 4 ใบ | 4 (GPU ละ 1 ตัว) · สะสมตัวละ 2 ใบ |
| เวลาเทรน 400 ใบ (50 ครั้ง) | **334 วินาที** (5 นาที 34 วินาที) | **261 วินาที** (4 นาที 21 วินาที) |
| เวลาทั้งรอบ รวมโหลดโมเดล | 407 วินาที | 353 วินาที |
| loss ช่วงต้น (เฉลี่ย 10 ครั้งแรก) | 0.0732 | 0.0735 |
| loss ช่วงท้าย (เฉลี่ย 10 ครั้งสุดท้าย) | 0.0426 | 0.0426 |
| VRAM สูงสุดต่อใบ | 15.73 GiB | 20.60 GiB |
| checksum ตรงกันทุก replica | ✅ ตรงทั้ง 2 ตัว (`ca9cc7ef…`) | ✅ ตรงทั้ง 4 ตัว (`abc563bb…`) |
| ขนาดไฟล์ adapter | 15.36 MB | 15.36 MB |

- **B was 22% faster than A.** Each B replica only needs 2 receipts before it sends its gradient, and 4 replicas work at the same time.
- **The loss is almost the same in both rounds.** Every update used the same 8 receipts in both rounds; only the way the work was split differs. The loss jumps around from one update to the next, depending on which 8 receipts were in it, so the table uses 10-update averages.
- **The link between the nodes stalled once in round B,** at update 21 (that update took 16.6 seconds). Training carried on to the end, and the stall is included in B's time.
- **Training kept running when SSH dropped.** Every process on the nodes ran under nohup, and the script running them retried the connection instead of treating a dropped link as finished.
- **Copying the results back was the hard part.** SSH from Node 1 to our side kept dropping, even for 30 MB. I sent the files from Node 1 to Node 2 over port 9000, then pulled them from Node 2. The sha256 of both adapters matches the files on Node 1.

Files are in `lab5_cluster_vlm`:
- `results/adapter_A` and `results/adapter_B`
- `results/raw/train_2node/`:
  - `losses.csv`: the loss of every update
  - `summary.json`
  - the logs and JSON of every replica
- new code: `code/run_train.sh` and `code/summarize_train.py`

🟢 **Both machines are still on and still billing.** vapp-lab5-n1 (instance <id>) costs $0.414 per hour and vapp-lab5-n2 (instance <id>) costs $0.510 per hour, so $0.924 per hour together.

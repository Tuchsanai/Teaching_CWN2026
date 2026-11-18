I wrote `vram_probe.py` and ran every case on the rented machine. The results are in `lab5_cluster_vlm/results/raw/vram_probe.json`.

**Test receipt:** the receipt with the longest answer in the Training Set is `train_000`. It has 22 line items and its answer JSON is 1,089 characters. The image is 853×1280 px, which gives 1,685 tokens per sample: 1,080 image tokens and 456 answer tokens. LoRA trains only 3.8 million parameters, and none of them are in the vision encoder.

| กรณี | จำนวน GPU | batch | Gradient Checkpointing | ผล | VRAM สูงสุดต่อใบ | วินาทีต่อ step |
|---|---|---|---|---|---|---|
| A · 1 ใบ | 1 | 1 | ปิด | **Out of Memory** ตั้งแต่ step 1 | 23.00 GiB (เต็มใบ) | – |
| A · 2 ใบ แบ่ง Layer 18/18 | 2 | 1 | ปิด | เทรนได้ | 14.50 / 15.73 GiB | 1.58 |
| A · 2 ใบ แบ่ง Layer 19/17 ✅ | 2 | 1 | ปิด | เทรนได้ | **15.14 / 15.08 GiB** | 1.55 |
| B · batch 1 | 1 | 1 | เปิด | เทรนได้ | 20.26 GiB | 1.60 |
| B · batch 2 | 1 | 2 | เปิด | **Out of Memory** ตั้งแต่ step 1 | 22.20 GiB (ขอเพิ่มอีก 1.91 GiB ไม่ได้) | – |

**Layer split for approach A:** the vision encoder and embeddings sit on GPU 0, and `lm_head` sits on GPU 1. With an even 18/18 split, GPU 1 peaked 1.2 GiB higher than GPU 0. I moved one layer to GPU 0 (19/17), and the two peaks came within 0.06 GiB of each other. Both runs are kept in the JSON file.

**น้ำหนักโมเดลใช้ VRAM เท่าไร:** 16.34 GiB, which is 69% of a 24 GB card. Before training even starts, only about 7 GiB is left.

**ที่เหลือใช้ไปกับอะไร:**
- **Activation (ส่วนใหญ่):** every layer's intermediate values are kept for the backward pass. With Gradient Checkpointing off, this needs more than 6.7 GiB, which is why a single GPU runs out of memory. With it on, it drops to about 3.9 GiB, but each layer is computed again during the backward pass.
- **Logits:** 1,685 tokens × 151,936 vocabulary × 4 bytes is about 1 GiB per sample. The 1.91 GiB that batch 2 failed to allocate is exactly the logits for 2 samples.
- **LoRA + gradient + optimizer state:** about 0.06 GiB, so almost nothing.

**แนวทาง A ต้องใช้ GPU กี่ใบ:** 2 GPUs per model copy. With the 19/17 split each card uses about 15 GiB, leaving roughly 8.5 GiB free. Speed is 1.55 seconds per step, about the same as one GPU because the two cards work in turn, not at the same time.

**แนวทาง B ป้อนได้ batch ละกี่ใบ:** 1 receipt per batch. With batch 2, memory runs out from the first step. So one GPU holds one model copy at batch 1, and a 2-GPU machine can run 2 copies at once.

**Problem on this machine:** the host driver is 535, and the image's CUDA 12.8 compatibility library made PyTorch fail to see the GPU (error 804). I fixed it by setting `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu` before running Python. The next steps on this machine will need the same setting.

🟢 **เครื่อง vapp-lab5-n1 (instance <id>, RTX 3090 × 2) ยังเปิดอยู่และคิดเงินอยู่ ราว $0.41 ต่อชั่วโมง**

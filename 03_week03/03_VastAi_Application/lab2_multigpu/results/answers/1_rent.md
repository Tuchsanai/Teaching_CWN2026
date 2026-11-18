I rented the 2× RTX 3090 machine `vapp-lab2` and it is still running. It became ready about 6 minutes after I rented it, inside the 10-minute limit, so I didn't need to delete it and try another one. I connected over SSH with the `devtoolSSH` key, and `nvidia-smi` and PyTorch both show 2 GPUs.

| Item | Value |
|---|---|
| GPU | 2× NVIDIA GeForce RTX 3090 (24 GB each) |
| Price per hour | **$0.414** (total incl. 60 GB disk, under the $0.60 cap) |
| Location | Estonia (EE) |
| CPU cores | 32 cores allocated to us (host has 64 threads, 2× Intel Xeon E5-2683 v4) |
| How the GPUs connect | **PCIe, no NVLink.** `nvidia-smi topo` reports PHB: data between the cards goes through the CPU's PCIe host bridge. PCIe 3.0 x8 per card. |
| Across CPU sockets? | **No.** Both GPUs are on NUMA node 1, the same CPU socket. |
| Image | `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime` (torch 2.8.0+cu128) |
| Status | **Running** (instance `<id>`, SSH `root@203.0.113.10 -p 41234`) |

**How I picked the machine:** verified, direct SSH (fixed IP), download ≥ 500 Mbps, ≥ 16 cores allocated, not in China. 8 machines matched, and this was the cheapest.

**Expect smaller gains with 2 GPUs:**
- **No direct GPU-to-GPU path:** PyTorch says peer-to-peer access between the two cards isn't available (`can_device_access_peer = False`). Data between GPUs has to pass through CPU memory.
- **PCIe 3.0 x8 is a narrow link.** In a 1 vs 2 GPU comparison, the 2-GPU speedup will fall short of 2×, especially for jobs that sync gradients often. That's actually a good point to show students.

The machine is billing $0.414/hr until it's deleted.

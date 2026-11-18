I closed everything for LAB 9: the vapp-lab9 machine is deleted and the web container is down.

**1. Machine vapp-lab9 (ID <id>): deleted**
- `vastai destroy instance <id> -y` worked. Listing the account again shows no vapp-lab9 left.

**2. Web container: closed**
- I ran `docker compose down` on project `vapp-lab9` (in `lab9_hybrid/code/web`). Container `vapp-lab9-web-1` and network `vapp-lab9_default` are both removed.
- This web ran on Windows (the host), not inside the `multi-account` container, because `/workspace/vastapp_lab` has no `code/web` folder.

## Actual cost of vapp-lab9
| Item | Value |
|---|---|
| Machine | RTX 3090 × 2 (in Korea), disk 50 GB |
| Lifetime | about **1 hr 37 min** (5,805 seconds, from rent to delete) |
| Price per hour | **$0.345/hr** (GPU $0.320 + disk $0.025), data transfer billed separately |
| GPU | 1.596 hr × $0.320 = **$0.511** |
| Disk | 1.616 hr × $0.025 = **$0.041** |
| Download | 7.2 GB × $0.003/GB = **$0.019** |
| Upload | 0.2 GB × $0.005/GB = **$0.001** |
| **Total** | **$0.572** (about 20 baht) |

These figures come from the account's own billing records (`vastai show invoices-v1 --charges`). Vast may still add a few cents for the last few seconds before deletion.

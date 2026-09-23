ตั้งตัวแปรก่อน (บรรทัด `Q=` อยู่ในหัวข้อ 3.1 ซึ่ง 3.2 และ 4.2 อ้างถึง):

```bash
Q='ร้านค้าลดราคา 10% เมื่อซื้อครบ 1000 บาท จงคำนวณยอดจ่ายสำหรับยอดซื้อ 999, 1000 และ 1500 บาท ตอบเป็นตารางยอดซื้อและยอดจ่ายทศนิยม 2 ตำแหน่ง ตามด้วยคำอธิบายสั้น ๆ และข้อควรระวัง 1 ข้อ ไม่ต้องสร้างไฟล์หรือรันคำสั่งอื่น'
```

| ค่าย | โมเดล | effort | คำสั่ง |
|---|---|---|---|
| Claude | Fable | low | `yolo1 --model fable --effort low -p "$Q"` |
| Claude | Fable | medium | `yolo1 --model fable --effort medium -p "$Q"` |
| Claude | Fable | high | `yolo1 --model fable --effort high -p "$Q"` |
| Claude | Fable | xhigh | `yolo1 --model fable --effort xhigh -p "$Q"` |
| Claude | Fable | max | `yolo1 --model fable --effort max -p "$Q"` |
| Claude | Opus | low | `yolo1 --model opus --effort low -p "$Q"` |
| Claude | Opus | medium | `yolo1 --model opus --effort medium -p "$Q"` |
| Claude | Opus | high | `yolo1 --model opus --effort high -p "$Q"` |
| Claude | Opus | xhigh | `yolo1 --model opus --effort xhigh -p "$Q"` |
| Claude | Opus | max | `yolo1 --model opus --effort max -p "$Q"` |
| Codex | Astra | low | `cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low "$Q"` |
| Codex | Astra | medium | `cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium "$Q"` |
| Codex | Astra | high | `cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=high "$Q"` |
| Codex | Astra | xhigh | `cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=xhigh "$Q"` |
| Codex | Astra | max | `cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=max "$Q"` |
| Codex | Sol | none | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=none "$Q"` |
| Codex | Sol | low | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=low "$Q"` |
| Codex | Sol | medium | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=medium "$Q"` |
| Codex | Sol | high | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=high "$Q"` |
| Codex | Sol | xhigh | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=xhigh "$Q"` |
| Codex | Sol | max | `cyolo1 exec --skip-git-repo-check --model gpt-6-sol -c model_reasoning_effort=max "$Q"` |
| Codex | Luna | none | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=none "$Q"` |
| Codex | Luna | low | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=low "$Q"` |
| Codex | Luna | medium | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=medium "$Q"` |
| Codex | Luna | high | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=high "$Q"` |
| Codex | Luna | xhigh | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=xhigh "$Q"` |
| Codex | Luna | max | `cyolo1 exec --skip-git-repo-check --model gpt-6-luna -c model_reasoning_effort=max "$Q"` |

**ชุดที่ไม่รองรับตามหัวข้อ 4.1** (ทั้ง 4 ชุด ไม่มีในตารางด้านบน):

- Astra + `none`
- Astra + `minimal`
- Sol + `minimal`
- Luna + `minimal`

หมายเหตุ: README ระบุว่าคำสั่ง Claude 10 คำสั่งและ Codex 17 คำสั่งรันจริงผ่านทั้งหมด และต้องครอบ `"$Q"` ด้วยเครื่องหมายคำพูดคู่เสมอ

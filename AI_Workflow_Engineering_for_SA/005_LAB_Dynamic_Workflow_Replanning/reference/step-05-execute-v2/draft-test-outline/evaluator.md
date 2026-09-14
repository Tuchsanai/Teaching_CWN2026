# Evaluator execution — verify-test-outline
REVIEW_MODE: artifacts; TASK_ID: draft-test-outline; VERIFY_TASK: verify-test-outline; RUN_ID: outline-v2-review; UTC: 2026-09-14T13:33:13.741164Z.
ผล: PASS_DOCUMENTS_ONLY; Mock/ระบบจริง NOT_TESTED; human rules BLOCKED. รายข้อและข้อสังเกตอยู่ test-outline-v2-check.md (53 บรรทัด).
ตรวจจริง: Python SHA-256/schema/UTC/unique IDs/DAG/scoped AC+locator+Flow comparison และอ่าน delta/regression; ไม่ใช้ browser, เว็บ, README, reveal-2 หรือ agent/AI CLI เพิ่ม.
หลักฐาน reuse: manifest แผน 29/29 และ Flow 26/26 ตรง; transfer byte-identical 2/2; AC v2 ตรง source 21/21 และคง AC v1 18/18; delta ตาราง US 18/18 เซลล์; Flow mapping 21/21.
ตรวจ hashes ก่อนเขียนซ้ำครบ; exclusive create ทุกไฟล์; ไม่แก้ plan/input/artifact/หลักฐานเดิม. ตรวจครั้งที่ 1; แก้ 0 รอบ.
ข้อค้าง: หมายเหตุ ก./ค./ช., state/ETA/refund/capacity/Unknown และ UI v2 runtime; ดูรายงานหลัก. ส่ง revise-ui ได้เฉพาะเอกสารตาม gates.

| Output ที่สร้างจริง (จากราก LAB) | SHA-256 |
|---|---|
| reference/session/evaluations/test-outline-v2-check.md | `0f982d0c0d6ee72264eca64f36bc6b0105edcaafab122f2d1654562d43cd3c2f` |
| reference/session/evaluations/plan-v2/outline-v2-review.md | `0f982d0c0d6ee72264eca64f36bc6b0105edcaafab122f2d1654562d43cd3c2f` |
| reference/step-05-execute-v2/draft-test-outline/evaluation/test-outline-v2-check.md | `0f982d0c0d6ee72264eca64f36bc6b0105edcaafab122f2d1654562d43cd3c2f` |
| reference/step-05-execute-v2/draft-test-outline/evaluation/evaluator.md | ไม่ทำ self-hash; hash หลังเขียนแสดงในผลเครื่องมือ |

Input-set SHA-256: `d96e4239b712e9b866235071a4436682d7ebbf3069dbb216fb4c3a04e5eaaa90` = UTF-8 ของ relative path+TAB+SHA256+LF เรียง path.
Manifest รวมไฟล์อ่านเนื้อหาและ dependency ที่อ่าน bytes เพื่อ hash เท่านั้น; ไม่อ้างตรวจเนื้อหาประวัติทั้งชุดซ้ำ.

| Input / dependency / target path จากราก LAB | SHA-256 |
|---|---|
| input/plan.schema.json | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` |
| reference/session/evaluations/flow-v1-check.md | `43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141` |
| reference/session/evaluations/flow-v2-check.md | `8eb49dba6953c6d63a3eb833f54a67c74bad9b42978a83ea97408d21e18f8c1d` |
| reference/session/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` |
| reference/session/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
| reference/session/evaluations/plan-v1-review.md | `f2facd03b3cd1f74969c110bfc336226b7d331f65042e51b036b5995166b3eb1` |
| reference/session/evaluations/plan-v1-validation.json | `a93dde889286710ef1217a542ab365b4fa27db3ca9e5473f9ed6dc57b83c5b1d` |
| reference/session/evaluations/plan-v2-review.md | `470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e` |
| reference/session/evaluations/plan-v2-validation.json | `a5b468a83cb2dde8ac5489f0c53214d28c68d41350cdd20e91e6a5c310bb25f3` |
| reference/session/evaluations/plan-v2/flow-v2-review-evidence.json | `b88498fd4c385582fbe9c52a3746e9d948944c3bb772fc880c6c9b9c88702f14` |
| reference/session/evaluations/plan-v2/plan-v2-review-evidence.json | `66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a` |
| reference/session/evaluations/test-outline-v1-check.md | `ea6c1f13c350bd5103493061d8b14fba8115cba46a8b900df42ec0445a1aa9a2` |
| reference/session/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` |
| reference/session/execution/plan-v1/audit-fr-baseline-run/audit-fr-baseline.md | `42318bb248f2a2e4b675cbdd5104f2bc70ea401ebd4d83aa29076b65113c77b8` |
| reference/session/execution/plan-v1/test-outline-run/draft-test-outline.md | `6ac65ca1a2cd45d5034c299677eab8b8545dcb6ac2257aada1c27cc0643814f8` |
| reference/session/execution/plan-v2/flow-v2-run/revise-flow.md | `860a4f6b24b83172708864633dba4368771d76473c3f8dc11e7d975e9f84f0a7` |
| reference/session/execution/plan-v2/fr-v2-run/revise-fr.md | `571c4226e328461c807411303a66737876618d768bcbc19d261b76a32dfd745b` |
| reference/session/execution/plan-v2/outline-v2-run/draft-test-outline.md | `dc9e94d3e20a7bf904c846b0f5fa6a30f9422b7828963168fc652be1e51d9eb4` |
| reference/session/flow-v2.md | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| reference/session/fr-nfr-v2.md | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| reference/session/impact-analysis-v2.md | `b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3` |
| reference/session/plan-v1.json | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| reference/session/plan-v1.md | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| reference/session/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| reference/session/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| reference/session/state-machine-v2.md | `efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a` |
| reference/session/structure-v2.md | `f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d` |
| reference/session/test-outline-v1.md | `6bdeccb7cf14fcdf03f0fa56578e1595c1ec3ea2dda67c3f74d4bba4c07ae18c` |
| reference/session/test-outline-v2.md | `50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763` |
| reference/step-00-input/baseline-filtered-v2/flow-check.json | `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` |
| reference/step-00-input/baseline-filtered-v2/flow.md | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` |
| reference/step-00-input/baseline-filtered-v2/fr-check.json | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` |
| reference/step-00-input/baseline-filtered-v2/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| reference/step-00-input/baseline-filtered-v2/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| reference/step-00-input/baseline-filtered-v2/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| reference/step-00-input/baseline-filtered-v2/state-machine.md | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` |
| reference/step-00-input/baseline-filtered-v2/structure.md | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` |
| reference/step-00-input/baseline-filtered-v2/ui-check.json | `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` |
| reference/step-00-input/baseline-filtered-v2/ui-contract.md | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` |
| reference/step-00-input/baseline-filtered-v2/ui-mockup.html | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` |
| reference/step-00-input/baseline-filtered-v2/us-initial.md | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` |
| reference/step-03-reveal-1/reveal-1.md | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` |
| reference/step-05-execute-v2/draft-test-outline/artifact-transfer.json | `b9737c4ff62085a7d8f74d2d6f51e1820c6ad233372268f009ab278d64917f03` |
| reference/step-05-execute-v2/draft-test-outline/execution.md | `dc9e94d3e20a7bf904c846b0f5fa6a30f9422b7828963168fc652be1e51d9eb4` |
| reference/step-05-execute-v2/draft-test-outline/test-outline-v2.md | `50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763` |

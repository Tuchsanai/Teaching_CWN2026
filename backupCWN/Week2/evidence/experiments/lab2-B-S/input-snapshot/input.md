# ชุด B — snapshot จากบริการฝึกจริง (ไม่ใช่ผลกู้คืนของ AI)

สองเหตุการณ์แยกกัน: รอบง่ายหนึ่งสาเหตุ และรอบต่อยอดหนึ่งสาเหตุ ให้ AI วินิจฉัยทั้งสองจากข้อมูลก่อนกู้เท่านั้น

## รอบ basic เก็บจริง UTC 2026-09-12T13:34:44.562Z

[B-S1] คำสั่ง ./shop status: STOPPED version=v1

[B-S2] Browser URL http://127.0.0.1:18762: page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:18762/
Call log:
[2m  - navigating to "http://127.0.0.1:18762/", waiting until "load"[22m


[B-S3] ./shop logs:
```text
{"utc": "2026-09-12T13:34:44.733025+00:00", "version": "v1", "scenario": "basic-B", "event": "RESET"}
{"utc": "2026-09-12T13:34:44.733062+00:00", "version": "v1", "scenario": "basic-B", "event": "SERVICE_STOPPED", "cause": "SERVICE_NOT_STARTED"}
```

## รอบ advanced เก็บจริง UTC 2026-09-12T13:34:47.491Z

[B-U1] คำสั่ง ./shop status: RUNNING version=v2 bookings=0

[B-U2] Browser URL http://127.0.0.1:18762: จองไม่สำเร็จ: รุ่น v2 จองสินค้าไม่ได้ (UPDATE_V2_BOOKING_BROKEN)

[B-U3] ./shop logs:
```text
{"utc": "2026-09-12T13:34:47.662255+00:00", "version": "v2", "scenario": "advanced-B", "event": "RESET"}
{"utc": "2026-09-12T13:34:47.798252+00:00", "version": "v2", "scenario": "advanced-B", "event": "STARTED"}
{"utc": "2026-09-12T13:34:47.831682+00:00", "version": "v2", "scenario": "advanced-B", "event": "UPDATE_APPLIED", "cause": "UPDATE_V2_BOOKING_BROKEN"}
{"utc": "2026-09-12T13:34:48.413324+00:00", "version": "v2", "scenario": "advanced-B", "event": "BOOKING_ERROR", "cause": "UPDATE_V2_BOOKING_BROKEN"}
```

หมายเหตุ: ยังไม่มีผลหลังทำใน input นี้ ให้ระบุผลคาดหวังและช่องรอคนตรวจ ห้ามอ้างว่ากู้คืนสำเร็จแล้ว

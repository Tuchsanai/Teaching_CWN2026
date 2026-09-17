# N1b — Explicit demo defaults (not input requirements)
The input specifies capabilities but no room dataset, persistence policy or booking rules. These are declared mock-up assumptions; illustrative numbers are not factual room inventory or organization rules.
- Demo dataset only: room `room-a` named ห้องอรุณ, capacity 6, equipment จอแสดงผล / ไวท์บอร์ด; `room-b` named ห้องนภา, capacity 10, equipment จอแสดงผล / วิดีโอคอล; `room-c` named ห้องพฤกษ์, capacity 4, equipment ไวท์บอร์ด. UI explicitly labels ข้อมูลห้องตัวอย่าง.
- Initial bookings empty. User can book as a local demo without authentication. Topic required only to identify demo bookings.
- Defaults: device-local current calendar date, 09:00–10:00 as editable example values; any valid same-day start/end is permitted, including past dates. No operating hours or duration limits are invented.
- A valid booking is immediately ยืนยันแล้ว; cancelling is immediate and retains ยกเลิกแล้ว history. No approval, fees or cancellation deadline.
- Overlapping confirmed intervals in same room/date are prevented; endpoints may touch. This is the chosen availability interpretation for this mock-up, not an asserted external policy.
- Save only in localStorage under `meeting-room-demo-v1`. On unavailable storage keep session memory and display a clear Thai notice that reload may lose changes. This is not a shared server/multiuser system. Safely ignore invalid saved records.
- UI Thai, system fonts. CSS room illustrations depict sample meeting spaces with no remote assets. Header/footer describes local demo storage.
- “Within 2 clicks” means opening each feature, not all form entry plus submission. Report click counts for access and separate full interaction counts to keep this distinction explicit. For cancel, precondition is a booking created via UI; from home nav bookings then cancel = 2 clicks.

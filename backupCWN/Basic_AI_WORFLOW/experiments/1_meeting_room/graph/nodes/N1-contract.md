# N1 — Interface contract

## Features and screens
All UI copy Thai. Home is `screen-rooms` (แสดงห้องประชุม), initially visible. Other screens hidden with the HTML `hidden` attribute: `screen-availability` (ดูเวลาว่าง), `screen-book` (จองห้อง), `screen-bookings` (สถานะและยกเลิกการจอง).
Persistent navigation buttons: `nav-rooms`, `nav-availability`, `nav-book`, `nav-bookings`. Each opens its corresponding screen in one click from home. Active nav has `aria-current="page"`. Navigation does not reload the document.
Navigation map: home → rooms (0 clicks); home → availability (1); home → booking form (1); home → bookings/status (1); home → bookings → cancellation action (2, given an existing confirmed booking). Access clicks are distinguished from form filling/submission; tests report both. All navigation controls visible on desktop and mobile; no collapsed menu.

## Static DOM owned by N3
- `app-notice`: global role=status, aria-live=polite, initially empty.
- `screen-rooms`: heading, `room-list` dynamic cards container, optional overview text; no hardcoded room cards.
- `screen-availability`: `availability-form`, `availability-room` select, `availability-date` date input, `availability-start` time input, `availability-end` time input, `availability-submit` submit button (ตรวจเวลาว่าง), `availability-result` role=status, `availability-schedule` dynamic list of all confirmed intervals for selected room/date. All form fields labeled and required. End > start validated by N2.
- `screen-book`: `booking-form`, `booking-room` select, `booking-date` date input, `booking-start` time input, `booking-end` time input, `booking-title` required text input (หัวข้อการประชุม), `booking-submit` submit button (ยืนยันการจอง), `booking-result` role=status.
- `screen-bookings`: `booking-list` dynamic cards; initial empty state rendered by N2.
No JavaScript or inline event attributes in N3. N3 delivers a complete HTML template with exactly `<!-- APP_SCRIPT -->` before closing body. CSS inline. System fonts, CSS graphics/inline SVG only, no external URLs/images/fonts/network. CSS must support dynamic markup below, hidden attribute with `[hidden]{display:none!important}`, responsive ≥360px.

## Dynamic DOM owned by N2
Room cards: `room-card-{roomId}` with name, capacity, equipment and button `room-book-{roomId}` (จองห้องนี้) opens booking form with matching room selected; button `room-availability-{roomId}` (ดูเวลาว่าง) opens availability with matching room selected. Classes `.room-card`, `.room-art`, `.room-info`, `.room-meta`, `.room-actions`, `.button`, `.button-primary`, `.button-secondary`, `.badge` available to N3.
Booking cards: `booking-card-{bookingId}`, `data-booking-id`, class `.booking-card`; children display title, room, date, start/end, status element `booking-status-{bookingId}`, class `.status-badge` plus `.status-confirmed` or `.status-cancelled`; status text ยืนยันแล้ว or ยกเลิกแล้ว; confirmed cards have button `cancel-booking-{bookingId}` text ยกเลิกการจอง. Cancelled cards retain status and have no actionable cancel button. Empty state `.empty-state`.
Availability result must include ว่าง or ไม่ว่าง; malformed interval message includes เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น. Availability schedule shows booked intervals or ยังไม่มีการจอง. Booking success includes จองสำเร็จ; conflict includes ช่วงเวลานี้ถูกจองแล้ว; invalid interval includes เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น; cancellation notice includes ยกเลิกการจองแล้ว. Insert user strings with textContent/createElement, never unsafe HTML interpolation.
After success, stay on booking form and expose success message; navigating bookings displays saved entry. On cancel stay bookings, immediately update status, release interval; refresh schedule/result on recheck.

## Data and JS interface owned by N2
Expose `window.MeetingApp` with:
- `listRooms()` → cloned array of `{id,name,capacity,equipment:[]}`.
- `checkAvailability(roomId,date,start,end)` → `{available:boolean, conflicts:Booking[], error?:string}`. Invalid fields return available=false and error.
- `createBooking({roomId,date,start,end,title})` → `{ok:true,booking:Booking}` or `{ok:false,error:string}`.
- `cancelBooking(bookingId)` → `{ok:true,booking:Booking}` or `{ok:false,error:string}`.
- `getBookingStatus(bookingId)` → 'confirmed' | 'cancelled' | null.
- `listBookings()` → cloned Booking array.
- `navigate(screenId)` using the exact screen IDs above.
- `init()` wires DOM once; call automatically after inline script at bottom of body.
Booking: `{id,roomId,date,start,end,title,status}` with unique ID, status confirmed/cancelled. No dependencies. Date YYYY-MM-DD and time HH:MM. Validate valid room, real calendar date, both times, nonempty trimmed title, start<end. Prevent overlap for same room/date where `newStart < existingEnd && newEnd > existingStart` and existing status confirmed. Cancelled bookings don't block time. Adjacent intervals allowed. No past-date rule, business-hour rule, approval workflow, authentication or arbitrary booking limits.

## N4 verification contract
Use installed Python `playwright.sync_api` and Chromium; open output.html using file://, no install/network. Test all 5 features via UI clicks, count trusted DOM click events from fresh home for each access route, capture values and assert ≤2. Seed booking precondition through UI for cancellation/status (not JS injection). Separate access clicks from full completion clicks with native input changes noted as data entry. Test successful creation, conflicting overlap, adjacent interval, invalid interval, cancellation visible status and released availability, persistence after reload, empty state, mobile layout and absence of network requests and JS pageerrors. Inspect live DOM before actions (record initial snapshot). Contract IDs are permitted selectors. Save results JSON and screenshots under artifacts; output failure details, never manufacture passing numbers. Tests callable `python nodes/N4-test.py`, configurable output target unnecessary. Avoid tests depending on N2/N3 implementation details beyond this contract.

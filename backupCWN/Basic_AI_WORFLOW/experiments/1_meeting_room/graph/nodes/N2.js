(function () {
  'use strict';

  const STORAGE_KEY = 'meeting-room-demo-v1';
  const rooms = [
    { id: 'room-a', name: 'ห้องอรุณ', capacity: 6, equipment: ['จอแสดงผล', 'ไวท์บอร์ด'] },
    { id: 'room-b', name: 'ห้องนภา', capacity: 10, equipment: ['จอแสดงผล', 'วิดีโอคอล'] },
    { id: 'room-c', name: 'ห้องพฤกษ์', capacity: 4, equipment: ['ไวท์บอร์ด'] }
  ];
  const screenIds = ['screen-rooms', 'screen-availability', 'screen-book', 'screen-bookings'];
  let bookings = [];
  let initialized = false;
  let storageUnavailable = false;
  let ignoredStorage = false;
  let sequence = 0;

  const byId = id => document.getElementById(id);
  const cloneBooking = booking => ({ ...booking });
  const findRoom = id => rooms.find(room => room.id === id);
  const overlaps = (left, right) => left.roomId === right.roomId && left.date === right.date &&
    left.start < right.end && left.end > right.start;

  function validDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const [year, month, day] = value.split('-').map(Number);
    if (year < 1 || month < 1 || month > 12 || day < 1) return false;
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    return day <= [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
  }

  function validTime(value) {
    return typeof value === 'string' && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(value);
  }

  function intervalError(roomId, date, start, end) {
    if (!findRoom(roomId)) return 'กรุณาเลือกห้องประชุมที่มีอยู่ในรายการ';
    if (!validDate(date)) return 'กรุณาระบุวันที่ให้ถูกต้อง';
    if (!validTime(start) || !validTime(end)) return 'กรุณาระบุเวลาเริ่มต้นและเวลาสิ้นสุดให้ถูกต้อง';
    if (start >= end) return 'เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น';
    return null;
  }

  function restore() {
    let raw;
    try { raw = window.localStorage.getItem(STORAGE_KEY); }
    catch (_) { storageUnavailable = true; return; }
    if (raw === null) return;
    let saved;
    try { saved = JSON.parse(raw); }
    catch (_) { ignoredStorage = true; return; }
    if (!Array.isArray(saved)) { ignoredStorage = true; return; }
    const ids = new Set();
    for (const item of saved) {
      if (!item || typeof item !== 'object' || Array.isArray(item) ||
          typeof item.id !== 'string' || !/^booking-[A-Za-z0-9-]+$/.test(item.id) ||
          ids.has(item.id) || intervalError(item.roomId, item.date, item.start, item.end) ||
          typeof item.title !== 'string' || !item.title.trim() ||
          !['confirmed', 'cancelled'].includes(item.status)) {
        ignoredStorage = true;
        continue;
      }
      const booking = {
        id: item.id, roomId: item.roomId, date: item.date,
        start: item.start, end: item.end, title: item.title.trim(), status: item.status
      };
      if (booking.status === 'confirmed' && bookings.some(existing =>
        existing.status === 'confirmed' && overlaps(booking, existing))) {
        ignoredStorage = true;
        continue;
      }
      ids.add(booking.id);
      bookings.push(booking);
    }
  }

  function notice(message = '') {
    const parts = [message];
    if (storageUnavailable) parts.push('ไม่สามารถบันทึกในเบราว์เซอร์ได้ ข้อมูลยังใช้ได้ในครั้งนี้ แต่การโหลดหน้าใหม่อาจทำให้ข้อมูลสูญหาย');
    if (ignoredStorage) parts.push('ข้ามข้อมูลที่บันทึกไว้ซึ่งไม่ถูกต้องแล้ว คุณสามารถใช้งานรายการที่ถูกต้องต่อได้');
    const target = byId('app-notice');
    if (target) target.textContent = parts.filter(Boolean).join(' · ');
  }

  function persist() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(bookings));
      storageUnavailable = false;
      ignoredStorage = false;
    } catch (_) { storageUnavailable = true; }
    notice();
  }

  function checkAvailability(roomId, date, start, end) {
    const error = intervalError(roomId, date, start, end);
    if (error) return { available: false, conflicts: [], error };
    const requested = { roomId, date, start, end };
    const conflicts = bookings.filter(booking => booking.status === 'confirmed' && overlaps(requested, booking));
    return { available: conflicts.length === 0, conflicts: conflicts.map(cloneBooking) };
  }

  function nextId() {
    let id;
    do {
      sequence += 1;
      id = 'booking-' + Date.now().toString(36) + '-' + sequence.toString(36);
    } while (bookings.some(booking => booking.id === id));
    return id;
  }

  function createBooking(input) {
    if (!input || typeof input !== 'object') return { ok: false, error: 'กรุณากรอกข้อมูลการจองให้ครบถ้วน' };
    const { roomId, date, start, end, title } = input;
    const availability = checkAvailability(roomId, date, start, end);
    if (availability.error) return { ok: false, error: availability.error };
    if (typeof title !== 'string' || !title.trim()) return { ok: false, error: 'กรุณาระบุหัวข้อการประชุม' };
    if (!availability.available) return { ok: false, error: 'ช่วงเวลานี้ถูกจองแล้ว กรุณาเลือกเวลาอื่นหรือห้องประชุมอื่น' };
    const booking = { id: nextId(), roomId, date, start, end, title: title.trim(), status: 'confirmed' };
    bookings.push(booking);
    persist();
    if (initialized) { renderBookings(); renderSchedule(); }
    return { ok: true, booking: cloneBooking(booking) };
  }

  function cancelBooking(bookingId) {
    const booking = bookings.find(item => item.id === bookingId);
    if (!booking) return { ok: false, error: 'ไม่พบรายการจองนี้' };
    if (booking.status === 'cancelled') return { ok: false, error: 'รายการจองนี้ถูกยกเลิกแล้ว' };
    booking.status = 'cancelled';
    persist();
    if (initialized) { renderBookings(); renderSchedule(); }
    notice('ยกเลิกการจองแล้ว ช่วงเวลานี้เปิดให้จองได้อีกครั้ง');
    return { ok: true, booking: cloneBooking(booking) };
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function button(id, text, className, handler) {
    const node = element('button', 'button ' + className, text);
    node.id = id;
    node.type = 'button';
    node.addEventListener('click', handler);
    return node;
  }

  function prettyDate(date) {
    const [year, month, day] = date.split('-').map(Number);
    const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
    return day + ' ' + months[month - 1] + ' ' + (year + 543);
  }

  function navigate(screenId) {
    if (!screenIds.includes(screenId)) return;
    for (const id of screenIds) {
      const screen = byId(id);
      if (screen) screen.hidden = id !== screenId;
      const nav = byId(id.replace('screen-', 'nav-'));
      if (nav) {
        if (id === screenId) nav.setAttribute('aria-current', 'page');
        else nav.removeAttribute('aria-current');
      }
    }
    if (screenId === 'screen-bookings') renderBookings();
    if (screenId === 'screen-availability') renderSchedule();
    const screen = byId(screenId);
    const heading = screen && screen.querySelector('h1, h2');
    if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true }); }
  }

  function renderRooms() {
    const container = byId('room-list');
    if (!container) return;
    container.replaceChildren();
    for (const room of rooms) {
      const card = element('article', 'room-card');
      card.id = 'room-card-' + room.id;
      const art = element('div', 'room-art');
      art.setAttribute('aria-hidden', 'true');
      art.dataset.room = room.id;
      art.append(element('div', 'room-window'), element('div', 'room-table'), element('div', 'room-chair room-chair-left'), element('div', 'room-chair room-chair-right'), element('div', 'room-plant'));
      const info = element('div', 'room-info');
      info.append(element('span', 'badge', 'ข้อมูลห้องตัวอย่าง'), element('h3', '', room.name));
      const meta = element('div', 'room-meta');
      meta.append(element('p', '', 'รองรับ ' + room.capacity + ' คน'), element('p', '', room.equipment.join(' · ')));
      const actions = element('div', 'room-actions');
      actions.append(
        button('room-book-' + room.id, 'จองห้องนี้', 'button-primary', () => {
          byId('booking-room').value = room.id;
          setResult('booking-result', '');
          navigate('screen-book');
        }),
        button('room-availability-' + room.id, 'ดูเวลาว่าง', 'button-secondary', () => {
          byId('availability-room').value = room.id;
          setResult('availability-result', '');
          navigate('screen-availability');
        })
      );
      info.append(meta, actions);
      card.append(art, info);
      container.append(card);
    }
  }

  function renderBookings() {
    const container = byId('booking-list');
    if (!container) return;
    container.replaceChildren();
    if (!bookings.length) {
      const empty = element('div', 'empty-state');
      empty.append(element('h3', '', 'ยังไม่มีรายการจอง'), element('p', '', 'เลือกห้องและเวลาที่สะดวก แล้วเริ่มจองห้องประชุมของคุณได้เลย'));
      empty.append(button('empty-book', 'จองห้องประชุม', 'button-primary', () => navigate('screen-book')));
      container.append(empty);
      return;
    }
    for (const booking of [...bookings].reverse()) {
      const card = element('article', 'booking-card');
      card.id = 'booking-card-' + booking.id;
      card.dataset.bookingId = booking.id;
      const info = element('div', 'booking-info');
      info.append(element('h3', '', booking.title), element('p', 'booking-meta', findRoom(booking.roomId).name + ' · ' + prettyDate(booking.date)), element('p', 'booking-time', booking.start + '–' + booking.end + ' น.'));
      const status = element('span', 'status-badge status-' + booking.status, booking.status === 'confirmed' ? 'ยืนยันแล้ว' : 'ยกเลิกแล้ว');
      status.id = 'booking-status-' + booking.id;
      const actions = element('div', 'booking-actions');
      actions.append(status);
      if (booking.status === 'confirmed') {
        actions.append(button('cancel-booking-' + booking.id, 'ยกเลิกการจอง', 'button-secondary', () => {
          const result = cancelBooking(booking.id);
          if (!result.ok) notice(result.error);
          else {
            const updated = byId('booking-status-' + booking.id);
            if (updated) { updated.tabIndex = -1; updated.focus({ preventScroll: true }); }
          }
        }));
      }
      card.append(info, actions);
      container.append(card);
    }
  }

  function renderSchedule() {
    const container = byId('availability-schedule');
    const roomInput = byId('availability-room');
    const dateInput = byId('availability-date');
    if (!container || !roomInput || !dateInput) return;
    container.replaceChildren();
    if (!findRoom(roomInput.value) || !validDate(dateInput.value)) {
      container.append(element('p', 'empty-state', 'เลือกห้องประชุมและวันที่เพื่อดูตารางการจอง'));
      return;
    }
    const matching = bookings.filter(booking => booking.status === 'confirmed' && booking.roomId === roomInput.value && booking.date === dateInput.value).sort((left, right) => left.start.localeCompare(right.start));
    container.append(element('h3', '', 'ตารางการจอง · ' + findRoom(roomInput.value).name + ' · ' + prettyDate(dateInput.value)));
    if (!matching.length) {
      container.append(element('p', 'empty-state', 'ยังไม่มีการจอง เลือกช่วงเวลาที่ต้องการได้เลย'));
      return;
    }
    const list = element('ul', 'schedule-list');
    for (const booking of matching) {
      const item = element('li', 'schedule-item');
      item.append(element('strong', 'schedule-time', booking.start + '–' + booking.end + ' น.'), element('span', 'schedule-title', ' · ' + booking.title), element('span', 'status-badge status-confirmed', 'ยืนยันแล้ว'));
      list.append(item);
    }
    container.append(list);
  }

  function setResult(id, message, kind) {
    const target = byId(id);
    if (!target) return;
    target.textContent = message;
    if (kind) target.dataset.state = kind;
    else delete target.dataset.state;
  }

  function currentDate() {
    const now = new Date();
    return String(now.getFullYear()).padStart(4, '0') + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
  }

  function init() {
    if (initialized) return;
    initialized = true;
    for (const prefix of ['availability', 'booking']) {
      const select = byId(prefix + '-room');
      if (select) {
        select.replaceChildren();
        for (const room of rooms) {
          const option = element('option', '', room.name + ' · ' + room.capacity + ' คน');
          option.value = room.id;
          select.append(option);
        }
      }
      const defaults = { date: currentDate(), start: '09:00', end: '10:00' };
      for (const [field, value] of Object.entries(defaults)) {
        const input = byId(prefix + '-' + field);
        if (input) input.value = value;
      }
      for (const field of ['room', 'date', 'start', 'end', ...(prefix === 'booking' ? ['title'] : [])]) {
        const input = byId(prefix + '-' + field);
        if (input) input.addEventListener('input', () => {
          setResult(prefix + '-result', '');
          if (prefix === 'availability') renderSchedule();
        });
      }
    }
    for (const screenId of screenIds) {
      const nav = byId(screenId.replace('screen-', 'nav-'));
      if (nav) nav.addEventListener('click', event => { event.preventDefault(); navigate(screenId); });
    }
    const availabilityForm = byId('availability-form');
    if (availabilityForm) availabilityForm.addEventListener('submit', event => {
      event.preventDefault();
      const roomId = byId('availability-room').value;
      const date = byId('availability-date').value;
      const start = byId('availability-start').value;
      const end = byId('availability-end').value;
      const result = checkAvailability(roomId, date, start, end);
      const message = result.error || (result.available
        ? 'ว่าง · ' + findRoom(roomId).name + ' วันที่ ' + prettyDate(date) + ' เวลา ' + start + '–' + end + ' น. สามารถจองได้'
        : 'ไม่ว่าง · ช่วงเวลานี้มีการจองแล้ว ' + result.conflicts.map(booking => booking.start + '–' + booking.end + ' น.').join(', ') + ' กรุณาเลือกช่วงเวลาอื่น');
      setResult('availability-result', message, result.error ? 'error' : result.available ? 'success' : 'error');
      renderSchedule();
    });
    const bookingForm = byId('booking-form');
    if (bookingForm) bookingForm.addEventListener('submit', event => {
      event.preventDefault();
      const result = createBooking({
        roomId: byId('booking-room').value, date: byId('booking-date').value,
        start: byId('booking-start').value, end: byId('booking-end').value,
        title: byId('booking-title').value
      });
      if (result.ok) {
        const booking = result.booking;
        setResult('booking-result', 'จองสำเร็จ · ' + findRoom(booking.roomId).name + ' วันที่ ' + prettyDate(booking.date) + ' เวลา ' + booking.start + '–' + booking.end + ' น. ยืนยันแล้ว ดูรายการได้ที่สถานะและยกเลิกการจอง', 'success');
      } else setResult('booking-result', result.error, 'error');
    });
    renderRooms();
    renderBookings();
    renderSchedule();
    navigate('screen-rooms');
    notice();
  }

  restore();
  window.MeetingApp = {
    listRooms: () => rooms.map(room => ({ ...room, equipment: [...room.equipment] })),
    checkAvailability,
    createBooking,
    cancelBooking,
    getBookingStatus: bookingId => {
      const booking = bookings.find(item => item.id === bookingId);
      return booking ? booking.status : null;
    },
    listBookings: () => bookings.map(cloneBooking),
    navigate,
    init
  };
  init();
})();

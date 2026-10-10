// BR-02 ช่วงเวลา [start, end) ซ้อนกัน = จองไม่ได้ · ต่อกันพอดี (จบ = เริ่ม) จองได้

export function overlaps(aStart: number, aEnd: number, bStart: number, bEnd: number): boolean {
  return aStart < bEnd && bStart < aEnd;
}

export interface BusySlot {
  therapistId: number;
  start: number;
  end: number;
}

/** นักบำบัดที่ว่างทั้งช่วง เรียง id น้อยไปมาก (D7) */
export function freeTherapists(candidateIds: number[], busy: BusySlot[], start: number, end: number): number[] {
  return [...candidateIds]
    .sort((a, b) => a - b)
    .filter((id) => !busy.some((b) => b.therapistId === id && overlaps(start, end, b.start, b.end)));
}

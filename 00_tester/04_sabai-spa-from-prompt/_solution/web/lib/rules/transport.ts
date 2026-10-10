// BR-17 ค่ารถ ≤ 5 กม. ฟรี · > 5 ถึง ≤ 15 กม. ฿300/คัน · > 15 กม. ไม่รับ · BR-18 คันละไม่เกิน 4 คน

export const FREE_KM_TENTHS = 50;
export const MAX_KM_TENTHS = 150;
export const FEE_PER_VEHICLE = 300_00;
export const SEATS_PER_VEHICLE = 4;

export function vehiclesFor(people: number): number {
  return Math.ceil(people / SEATS_PER_VEHICLE);
}

export type TransportQuote =
  | { ok: true; distanceKm: number; vehicles: number; perVehicle: number; fee: number }
  | { ok: false; code: "OUT_OF_AREA" | "BAD_DISTANCE" };

/** includedInPackage = แพ็กเกจที่รวมรถแล้ว (BR-19, A15) */
export function transportQuote(distanceKm: number, people: number, includedInPackage = false): TransportQuote {
  if (typeof distanceKm !== "number" || !Number.isFinite(distanceKm) || distanceKm < 0) return { ok: false, code: "BAD_DISTANCE" };
  const tenths = Math.round(distanceKm * 10);
  if (tenths > MAX_KM_TENTHS) return { ok: false, code: "OUT_OF_AREA" };
  const vehicles = vehiclesFor(people);
  const perVehicle = includedInPackage || tenths <= FREE_KM_TENTHS ? 0 : FEE_PER_VEHICLE;
  return { ok: true, distanceKm: tenths / 10, vehicles, perVehicle, fee: perVehicle * vehicles };
}

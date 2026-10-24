// BR-04 จองคู่ 2 คนพอดี · BR-05 กลุ่ม 3–6 คน 7 คนขึ้นไปโทรหาร้าน

export type BookingType = "single" | "couple" | "group" | "package" | "course";
export const BOOKING_TYPES: BookingType[] = ["single", "couple", "group", "package", "course"];

export const GROUP_MIN = 3;
export const GROUP_MAX = 6;
export const COUPLE_SIZE = 2;

export type PartyError = "SINGLE_ONE" | "COUPLE_NEEDS_2" | "GROUP_TOO_SMALL" | "GROUP_CALL_SHOP" | "BAD_PEOPLE";

export function checkParty(type: BookingType, people: number): PartyError | null {
  if (!Number.isInteger(people) || people < 1) return "BAD_PEOPLE";
  switch (type) {
    case "single":
    case "course":
      return people === 1 ? null : "SINGLE_ONE";
    case "couple":
      return people === COUPLE_SIZE ? null : "COUPLE_NEEDS_2";
    case "group":
      if (people > GROUP_MAX) return "GROUP_CALL_SHOP";
      return people >= GROUP_MIN ? null : "GROUP_TOO_SMALL";
    case "package":
      return people > GROUP_MAX ? "GROUP_CALL_SHOP" : null;
  }
}

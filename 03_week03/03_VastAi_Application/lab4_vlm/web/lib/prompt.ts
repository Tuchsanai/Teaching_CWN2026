// พรอมต์เดียวกับตอนเทรนและตอนวัดผล (scripts/receipt_common.py) — ต้องตรงกันทุกตัวอักษร
export const PROMPT =
  "Read this receipt and return ONLY one JSON object with exactly this schema:\n" +
  '{"items":[{"name":string,"qty":integer,"price":integer}],' +
  '"subtotal":integer|null,"tax":integer|null,"total":integer|null}\n' +
  "Rules: items = every purchased line in the order printed; price = the amount printed on that line; " +
  "qty = 1 when no quantity is printed; numbers are integers without thousands separators or currency " +
  '(for example "25,000" -> 25000); use null for a value that is not printed. ' +
  "No explanation and no markdown.";

export const MAX_SIDE = 1280; // ด้านยาวสุดของภาพที่ส่งให้โมเดล (เท่ากับตอนเทรน)

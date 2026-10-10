"use client";

import Link from "next/link";
import { useState } from "react";
import { formatBaht } from "@/lib/money.ts";
import { useI18n } from "./I18nProvider.tsx";

/** FR-21 / BR-19 ราคารวม = ฿2,900 × จำนวนคน (ยอดที่เก็บจริงคิดใหม่ที่เซิร์ฟเวอร์ตอนจอง) */
export function PackageCalc({ unitSatang }: { unitSatang: number }) {
  const { t } = useI18n();
  const [people, setPeople] = useState(2);
  return (
    <div className="thai-band">
      <div className="field">
        <label htmlFor="pk-people">{t("book.people")}</label>
        <select id="pk-people" value={people} onChange={(e) => setPeople(Number(e.target.value))} data-testid="package-people">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>
      <p className="price" data-testid="package-total" data-amount={(unitSatang * people) / 100}>
        {t("package.calc", { n: people })}: {formatBaht(unitSatang * people)}
      </p>
      <Link className="btn btn-gold" href={`/book?type=package&service=P01&people=${people}`} data-testid="package-book">
        {t("package.book")}
      </Link>
    </div>
  );
}

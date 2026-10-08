"use client";

import { useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { PageHead } from "@/components/Shared";

export default function PrivacyPage() {
  const { t } = useApp();
  useReady(true);
  return (
    <>
      <PageHead eyebrow={t("nav_privacy")} title={t("privacy_title")} />
      <section className="section">
        <div className="container--narrow prose">
          <p className="highlight" data-testid="privacy-no-face">
            <Icon name="shield" size={28} /> {t("privacy_noface")}
          </p>
          <h2>{t("privacy_h1")}</h2>
          <p>{t("privacy_p1")}</p>
          <h2>{t("privacy_h2")}</h2>
          <p data-testid="privacy-skin">{t("privacy_p2")}</p>
          <h2>{t("privacy_h3")}</h2>
          <p>{t("privacy_p3")}</p>
          <h2>{t("privacy_h4")}</h2>
          <p>{t("privacy_p4")}</p>
          <h2>{t("privacy_h5")}</h2>
          <p>{t("privacy_p5")}</p>
        </div>
      </section>
    </>
  );
}

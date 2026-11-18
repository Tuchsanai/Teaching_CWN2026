"use client";
import { usePathname } from "next/navigation";

export default function Nav() {
  const p = usePathname();
  const tab = (href: string, label: string) => (
    <a href={href} className={"tab" + (p.startsWith(href) ? " on" : "")}>{label}</a>
  );
  return <nav className="tabs">{tab("/read", "อ่านใบเสร็จ")}{tab("/expenses", "รายจ่าย")}</nav>;
}

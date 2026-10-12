// 3 ภาษา ไทย / English / 中文 (FR-24, NFR-06) · ภาษาที่เลือกเก็บใน cookie `lang`

export type Lang = "th" | "en" | "zh";
export const LANGS: Lang[] = ["th", "en", "zh"];
export const LANG_COOKIE = "lang";
export const SHOP_PHONE = "02-123-4567";

export function normalizeLang(v: unknown): Lang {
  return v === "en" || v === "zh" ? v : "th";
}

type Entry = { th: string; en: string; zh: string };

const D = {
  // ── ทั่วไป / เมนู ──
  brand: { th: "สบายใจ สปา", en: "Sabai Jai Wellness Spa", zh: "舒心水疗" },
  tagline: { th: "สปาไทยร่วมสมัย ผ่อนคลายทั้งกายและใจ", en: "Contemporary Thai spa for body and mind", zh: "当代泰式水疗，身心放松" },
  "nav.home": { th: "หน้าแรก", en: "Home", zh: "首页" },
  "nav.services": { th: "บริการ", en: "Services", zh: "服务项目" },
  "nav.book": { th: "จองคิว", en: "Book", zh: "预约" },
  "nav.package": { th: "แพ็กเกจ", en: "Package", zh: "套餐" },
  "nav.therapists": { th: "นักบำบัด", en: "Therapists", zh: "理疗师" },
  "nav.giftcard": { th: "Gift Card", en: "Gift Card", zh: "礼品卡" },
  "nav.transport": { th: "รถรับส่ง", en: "Shuttle", zh: "接送服务" },
  "nav.account": { th: "บัญชีของฉัน", en: "My account", zh: "我的账户" },
  "nav.wallet": { th: "คอร์สของฉัน", en: "My course", zh: "我的疗程" },
  "nav.chat": { th: "ผู้ช่วยแชท", en: "Chat assistant", zh: "聊天助手" },
  "nav.quiz": { th: "แบบทดสอบ", en: "Quiz", zh: "测试" },
  "nav.skin": { th: "วิเคราะห์ผิว", en: "Skin check", zh: "肌肤分析" },
  "nav.admin": { th: "หลังร้าน", en: "Back office", zh: "后台" },
  "nav.adminReport": { th: "รายงานยอด", en: "Sales report", zh: "销售报表" }, // CR-05
  "nav.login": { th: "เข้าสู่ระบบ", en: "Log in", zh: "登录" },
  "nav.logout": { th: "ออกจากระบบ", en: "Log out", zh: "退出" },
  "nav.menu": { th: "เมนู", en: "Menu", zh: "菜单" },
  "lang.label": { th: "เลือกภาษา", en: "Language", zh: "语言" },
  "music.play": { th: "เปิดเพลงสปา", en: "Play spa music", zh: "播放水疗音乐" },
  "music.stop": { th: "ปิดเพลงสปา", en: "Stop spa music", zh: "停止音乐" },
  "footer.hours": { th: "เปิดทุกวัน 10:00–22:00", en: "Open daily 10:00–22:00", zh: "每天营业 10:00–22:00" },
  "footer.phone": { th: "โทร", en: "Call", zh: "电话" },
  "common.minutes": { th: "นาที", en: "min", zh: "分钟" },
  "common.perPerson": { th: "ต่อคน", en: "per person", zh: "每人" },
  "common.herbs": { th: "สมุนไพร", en: "Herbs", zh: "草药" },
  "common.bookNow": { th: "จองเลย", en: "Book now", zh: "立即预约" },
  "common.loading": { th: "กำลังโหลด…", en: "Loading…", zh: "加载中…" },
  "common.close": { th: "ปิด", en: "Close", zh: "关闭" },
  "common.people": { th: "คน", en: "people", zh: "人" },
  "common.km": { th: "กม.", en: "km", zh: "公里" },
  "common.free": { th: "ฟรี", en: "Free", zh: "免费" },
  "common.skip": { th: "ข้ามไปที่เนื้อหา", en: "Skip to content", zh: "跳到内容" },
  "common.loginFirst": { th: "กรุณาเข้าสู่ระบบก่อน", en: "Please log in first", zh: "请先登录" },

  // ── หน้าแรก ──
  "home.title": { th: "ปล่อยใจให้สบาย ที่สบายใจ สปา", en: "Let your mind rest at Sabai Jai Spa", zh: "在舒心水疗放松身心" },
  "home.subtitle": { th: "นวดไทย สมุนไพรไทยแท้ เปิดทุกวัน 10:00–22:00 จองออนไลน์ได้ใน 4 ขั้น", en: "Thai massage with genuine Thai herbs. Open daily 10:00–22:00. Book online in 4 steps.", zh: "正宗泰式按摩与泰国草药。每天 10:00–22:00 营业，4 步在线预约。" },
  "home.ctaBook": { th: "จองคิวเลย", en: "Book a session", zh: "立即预约" },
  "home.ctaPackage": { th: "ดูแพ็กเกจ Bangkok Relax", en: "See Bangkok Relax package", zh: "查看曼谷放松套餐" },
  "home.moodTitle": { th: "วันนี้คุณรู้สึกอย่างไร?", en: "How do you feel today?", zh: "你今天感觉如何？" },
  "home.moodHint": { th: "เลือก 1 อารมณ์ เราแนะนำบริการให้", en: "Pick one mood and we will suggest services", zh: "选择一种心情，我们为您推荐" },
  "home.featured": { th: "บริการยอดนิยม", en: "Popular services", zh: "热门服务" },
  "home.explore": { th: "ค้นหาสิ่งที่ใช่สำหรับคุณ", en: "Find what suits you", zh: "找到适合你的" },
  "home.quizCta": { th: "ทำแบบทดสอบ 4 ข้อ", en: "Take the 4-question quiz", zh: "做4题小测试" },
  "home.skinCta": { th: "วิเคราะห์ผิวจากเซลฟี่", en: "Analyse skin from a selfie", zh: "自拍肌肤分析" },
  "home.chatCta": { th: "ถามผู้ช่วยแชท", en: "Ask the chat assistant", zh: "询问聊天助手" },
  "mood.stressed": { th: "เครียด", en: "Stressed", zh: "压力大" },
  "mood.tired": { th: "เหนื่อย", en: "Tired", zh: "疲惫" },
  "mood.aches": { th: "ปวดเมื่อย", en: "Achy", zh: "酸痛" },
  "mood.insomnia": { th: "นอนไม่หลับ", en: "Can't sleep", zh: "失眠" },
  "mood.result": { th: "บริการที่แนะนำสำหรับคุณ", en: "Recommended for you", zh: "为您推荐" },

  // ── บริการ ──
  "services.title": { th: "บริการทั้งหมด", en: "All services", zh: "全部服务" },
  "services.course": { th: "คอร์ส 11 ครั้ง ใช้ได้ 180 วัน", en: "11 sessions, valid 180 days", zh: "11次，有效期180天" },

  // ── จอง ──
  "book.title": { th: "จองคิว", en: "Book a session", zh: "预约" },
  "book.step1": { th: "บริการ", en: "Service", zh: "服务" },
  "book.step2": { th: "วัน/เวลา", en: "Date & time", zh: "日期时间" },
  "book.step3": { th: "ข้อมูลติดต่อ", en: "Contact", zh: "联系方式" },
  "book.step4": { th: "ยืนยัน", en: "Confirm", zh: "确认" },
  "book.stepOf": { th: "ขั้นที่ {n} จาก 4", en: "Step {n} of 4", zh: "第 {n} 步 / 共 4 步" },
  "book.type": { th: "แบบการจอง", en: "Booking type", zh: "预约类型" },
  "type.single": { th: "เดี่ยว", en: "Single", zh: "单人" },
  "type.couple": { th: "คู่ (Couple Suite)", en: "Couple (Couple Suite)", zh: "双人（情侣套房）" },
  "type.group": { th: "กลุ่ม 3–6 คน", en: "Group 3–6", zh: "团体 3–6 人" },
  "type.package": { th: "แพ็กเกจ", en: "Package", zh: "套餐" },
  "type.course": { th: "จองด้วยคอร์ส", en: "Book with course", zh: "用疗程预约" },
  "book.service": { th: "เลือกบริการ", en: "Choose a service", zh: "选择服务" },
  "book.people": { th: "จำนวนคน", en: "Number of people", zh: "人数" },
  "book.next": { th: "ถัดไป", en: "Next", zh: "下一步" },
  "book.back": { th: "ย้อนกลับ", en: "Back", zh: "返回" },
  "book.date": { th: "วันที่", en: "Date", zh: "日期" },
  "book.dateHint": { th: "จองได้ {min} ถึง {max}", en: "Available {min} to {max}", zh: "可预约 {min} 至 {max}" },
  "book.time": { th: "รอบเวลาที่ว่าง", en: "Available times", zh: "可选时段" },
  "book.noSlots": { th: "วันนี้ไม่มีรอบว่าง ลองเลือกวันอื่น", en: "No free times on this day, try another date", zh: "当天没有空闲时段，请换一天" },
  "book.therapist": { th: "นักบำบัด", en: "Therapist", zh: "理疗师" },
  "book.anyTherapist": { th: "ใครก็ได้ (ระบบจัดให้)", en: "Anyone (auto-assign)", zh: "任意（系统分配）" },
  "book.tour": { th: "ดูห้อง 360°", en: "View room 360°", zh: "360° 看房" },
  "book.tourTitle": { th: "ทัวร์ห้อง Couple Suite 360°", en: "Couple Suite 360° tour", zh: "情侣套房 360° 导览" },
  "book.tourHint": { th: "ลากเมาส์หรือปัดนิ้วเพื่อหมุนรอบห้อง", en: "Drag or swipe to look around", zh: "拖动或滑动以环顾房间" },
  "book.contactName": { th: "ชื่อผู้จอง", en: "Your name", zh: "姓名" },
  "book.contactPhone": { th: "เบอร์โทร", en: "Phone", zh: "电话" },
  "book.guestHint": { th: "ไม่ได้เข้าสู่ระบบ: จองด้วยชื่อ+เบอร์ได้ แต่ไม่ได้สะสมแต้ม", en: "Not logged in: you can book with name and phone, but you will not earn points", zh: "未登录：可用姓名和电话预约，但不累积积分" },
  "book.options": { th: "ส่วนลดและการชำระ", en: "Discounts & payment", zh: "优惠与付款" },
  "book.points": { th: "แลกแต้ม (100 แต้ม = ลด ฿50)", en: "Redeem points (100 pts = ฿50 off)", zh: "积分兑换（100 分 = 减 50 泰铢）" },
  "book.pointsHave": { th: "คุณมี {p} แต้ม แลกได้สูงสุด {b} ครั้ง", en: "You have {p} points, up to {b} redemptions", zh: "您有 {p} 积分，最多兑换 {b} 次" },
  "book.redeemBlocks": { th: "จำนวนครั้งที่แลก", en: "Redemptions", zh: "兑换次数" },
  "book.redeemNone": { th: "แต้มไม่พอแลก (ต้องมีอย่างน้อย 100 แต้ม)", en: "Not enough points (need at least 100)", zh: "积分不足（至少需要 100 分）" },
  "book.birthday": { th: "ใช้ส่วนลดเดือนเกิด 20%", en: "Use birthday-month 20% discount", zh: "使用生日月 20% 折扣" },
  "book.giftcard": { th: "รหัส Gift Card", en: "Gift card code", zh: "礼品卡代码" },
  "book.giftcardCheck": { th: "ใช้บัตรนี้", en: "Use this card", zh: "使用此卡" },
  "book.giftcardBalance": { th: "ยอดคงเหลือในบัตร {b}", en: "Card balance {b}", zh: "卡内余额 {b}" },
  "book.giftcardAfter": { th: "ยอดคงเหลือหลังใช้ {b}", en: "Balance after use {b}", zh: "使用后余额 {b}" },
  "book.transport": { th: "ต้องการรถรับส่งจากโรงแรม", en: "I need hotel pickup", zh: "需要酒店接送" },
  "book.hotel": { th: "เลือกโรงแรม", en: "Choose hotel", zh: "选择酒店" },
  "book.hotelOther": { th: "พิมพ์ระยะเอง", en: "Enter distance myself", zh: "自行输入距离" },
  "book.distance": { th: "ระยะทางจากโรงแรม (กม.)", en: "Distance from hotel (km)", zh: "距酒店距离（公里）" },
  "book.course": { th: "คอร์สที่ใช้", en: "Course to use", zh: "使用的疗程" },
  "book.courseNone": { th: "ไม่มีคอร์สที่ใช้ได้ (เหลือ 0 ครั้งหรือหมดอายุ)", en: "No usable course (0 sessions left or expired)", zh: "没有可用疗程（剩余0次或已过期）" },
  "book.courseLogin": { th: "จองด้วยคอร์สต้องเข้าสู่ระบบ", en: "Log in to book with a course", zh: "用疗程预约需要登录" },
  "book.summary": { th: "สรุปก่อนจ่าย", en: "Summary before payment", zh: "付款前汇总" },
  "book.herbsConfirm": { th: "สมุนไพรที่ใช้ในบริการนี้", en: "Herbs used in this service", zh: "本服务使用的草药" },
  "book.when": { th: "วันเวลา", en: "When", zh: "时间" },
  "line.gross": { th: "ราคาเต็ม", en: "Full price", zh: "原价" },
  "line.discount.group": { th: "ส่วนลดกลุ่ม {p}%", en: "Group discount {p}%", zh: "团体折扣 {p}%" },
  "line.discount.tier": { th: "ส่วนลดระดับสมาชิก {p}%", en: "Member discount {p}%", zh: "会员折扣 {p}%" },
  "line.discount.birthday": { th: "ส่วนลดเดือนเกิด {p}%", en: "Birthday discount {p}%", zh: "生日折扣 {p}%" },
  "line.points": { th: "แลกแต้ม {n} แต้ม", en: "Points redeemed {n}", zh: "积分兑换 {n} 分" },
  "line.transport": { th: "ค่ารถรับส่ง {v} คัน ({d} กม.)", en: "Shuttle {v} vehicle(s) ({d} km)", zh: "接送车 {v} 辆（{d} 公里）" },
  "line.transportIncluded": { th: "รวมในแพ็กเกจแล้ว", en: "included in package", zh: "已含在套餐内" },
  "line.total": { th: "ยอดสุทธิ", en: "Total", zh: "合计" },
  "line.giftcard": { th: "จ่ายด้วย Gift Card", en: "Paid by gift card", zh: "礼品卡支付" },
  "line.other": { th: "ชำระที่ร้าน / ช่องทางอื่น", en: "Pay at shop / other", zh: "到店/其他方式支付" },
  "line.earn": { th: "แต้มที่จะได้หลังใช้บริการ", en: "Points earned after the visit", zh: "服务完成后获得积分" },
  "line.course": { th: "ใช้คอร์ส 1 ครั้ง", en: "Uses 1 course session", zh: "使用疗程 1 次" },
  "book.confirm": { th: "ยืนยันการจอง", en: "Confirm booking", zh: "确认预约" },
  "book.confirmed": { th: "จองสำเร็จ! รหัสการจอง {code}", en: "Booking confirmed! Code {code}", zh: "预约成功！预约号 {code}" },
  "book.confirmedDetail": { th: "{service} · {when} · ยอด {total}", en: "{service} · {when} · total {total}", zh: "{service} · {when} · 金额 {total}" },
  "book.again": { th: "จองอีกครั้ง", en: "Book again", zh: "再次预约" },
  "book.callShop": { th: "โทรหาร้าน", en: "Call the shop", zh: "致电本店" },

  // ── แพ็กเกจ ──
  "package.title": { th: "แพ็กเกจ Bangkok Relax", en: "Bangkok Relax Package", zh: "曼谷放松套餐" },
  "package.price": { th: "{p} ต่อคน", en: "{p} per person", zh: "每人 {p}" },
  "package.includes": { th: "สิ่งที่ได้ 3 อย่าง", en: "3 things included", zh: "包含 3 项" },
  "package.item1": { th: "นวดไทย", en: "Thai massage", zh: "泰式按摩" },
  "package.item2": { th: "ประคบสมุนไพร", en: "Herbal compress", zh: "草药热敷" },
  "package.item3": { th: "รถรับส่งโรงแรม (ไม่เกิน 15 กม.)", en: "Hotel shuttle (up to 15 km)", zh: "酒店接送（15公里内）" },
  "package.calc": { th: "ราคารวม {n} คน", en: "Total for {n} people", zh: "{n} 人合计" },
  "package.note": { th: "ราคาแพ็กเกจตายตัว ไม่มีส่วนลดกลุ่ม/ระดับ/เดือนเกิด", en: "Fixed package price: no group, member or birthday discounts", zh: "套餐价格固定，不享团体/会员/生日折扣" },
  "package.book": { th: "จองแพ็กเกจ", en: "Book package", zh: "预订套餐" },

  // ── นักบำบัด ──
  "therapists.title": { th: "นักบำบัดของเรา", en: "Our therapists", zh: "我们的理疗师" },
  "therapists.filter": { th: "4.5 ดาวขึ้นไป", en: "4.5 stars and up", zh: "4.5 星及以上" },
  "therapists.reviews": { th: "{n} รีวิว", en: "{n} reviews", zh: "{n} 条评价" },
  "therapists.noReviews": { th: "ยังไม่มีรีวิว", en: "No reviews yet", zh: "暂无评价" },
  "therapists.does": { th: "บริการที่ทำได้", en: "Services", zh: "可做项目" },
  "therapists.count": { th: "แสดง {n} คน", en: "Showing {n}", zh: "显示 {n} 位" },

  // ── บัญชี ──
  "account.title": { th: "บัญชีของฉัน", en: "My account", zh: "我的账户" },
  "account.hello": { th: "สวัสดี {name}", en: "Hello {name}", zh: "你好 {name}" },
  "account.tier": { th: "ระดับสมาชิก", en: "Member tier", zh: "会员等级" },
  "tier.silver": { th: "Silver", en: "Silver", zh: "Silver" },
  "tier.gold": { th: "Gold", en: "Gold", zh: "Gold" },
  "tier.platinum": { th: "Platinum", en: "Platinum", zh: "Platinum" },
  "account.tierPct": { th: "ส่วนลด {p}%", en: "{p}% off", zh: "优惠 {p}%" },
  "account.spend": { th: "ยอดสะสม {s}", en: "Lifetime spend {s}", zh: "累计消费 {s}" },
  "account.next": { th: "อีก {x} ถึง {tier}", en: "{x} more to {tier}", zh: "还差 {x} 升级到 {tier}" },
  "account.top": { th: "อยู่ระดับสูงสุดแล้ว", en: "You are at the top tier", zh: "已是最高等级" },
  "account.points": { th: "แต้มคงเหลือ", en: "Points balance", zh: "积分余额" },
  "account.pointsUnit": { th: "{p} แต้ม", en: "{p} points", zh: "{p} 积分" },
  "account.birthdayOn": { th: "เดือนนี้เป็นเดือนเกิดของคุณ ใช้ส่วนลด 20% ได้ 1 ครั้ง (นัดภายในเดือนนี้)", en: "It's your birthday month: one 20% discount for an appointment this month", zh: "本月是您的生日月：本月预约可享一次 20% 折扣" },
  "account.birthdayUsed": { th: "ใช้สิทธิ์ส่วนลดเดือนเกิดของเดือนนี้แล้ว", en: "Birthday discount already used this month", zh: "本月生日折扣已使用" },
  "account.bookings": { th: "นัดและประวัติทรีตเมนต์", en: "Appointments & treatment history", zh: "预约与护理记录" },
  "account.noBookings": { th: "ยังไม่มีนัด", en: "No appointments yet", zh: "暂无预约" },
  "account.cancel": { th: "ยกเลิกนัด", en: "Cancel", zh: "取消预约" },
  "account.cancelConfirm": { th: "ยืนยันยกเลิก", en: "Confirm cancel", zh: "确认取消" },
  "account.cancelDone": { th: "ยกเลิกแล้ว", en: "Cancelled", zh: "已取消" },
  "account.cancelLate": { th: "เหลือน้อยกว่า 24 ชม. ยกเลิกเองไม่ได้ กรุณาโทรหาร้าน", en: "Less than 24 hours left. Please call the shop", zh: "不足24小时，无法自行取消，请致电本店" },
  "account.reschedule": { th: "เลื่อนนัด", en: "Reschedule", zh: "改期" },
  "account.rescheduleTitle": { th: "เลื่อนนัด {code}", en: "Reschedule {code}", zh: "改期 {code}" },
  "account.rescheduleDate": { th: "วันที่ใหม่", en: "New date", zh: "新日期" },
  "account.rescheduleSlots": { th: "เลือกรอบเวลา (นักบำบัดคนเดิม)", en: "Choose a time (same therapist)", zh: "选择时间（原理疗师）" },
  "account.rescheduleNoSlots": { th: "วันนี้ไม่มีรอบที่นักบำบัดคนเดิมว่าง", en: "No times available with the same therapist on this day", zh: "当天原理疗师没有空档" },
  "account.rescheduleConfirm": { th: "ยืนยันเลื่อนนัด", en: "Confirm reschedule", zh: "确认改期" },
  "account.rescheduleDone": { th: "เลื่อนนัด {code} เป็น {date} {time} แล้ว", en: "Booking {code} moved to {date} {time}", zh: "预约 {code} 已改至 {date} {time}" },
  "account.rescheduleClose": { th: "ปิด", en: "Close", zh: "关闭" },
  "account.paid": { th: "ราคาที่จ่าย", en: "Paid", zh: "实付" },
  "account.wallet": { th: "ดูคอร์ส / กราฟรอบเอว", en: "Course wallet & waist chart", zh: "疗程钱包与腰围图" },
  "status.confirmed": { th: "ยืนยัน", en: "Confirmed", zh: "已确认" },
  "status.cancelled": { th: "ยกเลิก", en: "Cancelled", zh: "已取消" },
  "status.completed": { th: "ใช้บริการแล้ว", en: "Completed", zh: "已完成" },

  // ── Wallet ──
  "wallet.title": { th: "คอร์สของฉัน (Wallet)", en: "My course wallet", zh: "我的疗程钱包" },
  "wallet.remaining": { th: "เหลือ {r} จาก {t} ครั้ง", en: "{r} of {t} sessions left", zh: "剩余 {r} / {t} 次" },
  "wallet.expires": { th: "หมดอายุ {d}", en: "Expires {d}", zh: "到期 {d}" },
  "wallet.daysLeft": { th: "อีก {n} วัน", en: "{n} days left", zh: "还剩 {n} 天" },
  "wallet.expired": { th: "หมดอายุแล้ว", en: "Expired", zh: "已过期" },
  "wallet.none": { th: "ยังไม่มีคอร์ส", en: "No course yet", zh: "暂无疗程" },
  "wallet.book": { th: "จองด้วยคอร์ส", en: "Book with course", zh: "用疗程预约" },
  "wallet.buy": { th: "ซื้อคอร์สกระชับสัดส่วน ฿15,000 (10 แถม 1)", en: "Buy body contouring course ฿15,000 (10 + 1 free)", zh: "购买塑形疗程 15,000 泰铢（买10送1）" },
  "wallet.bought": { th: "ซื้อคอร์สสำเร็จ หมดอายุ {d}", en: "Course purchased, expires {d}", zh: "购买成功，到期 {d}" },
  "wallet.waist": { th: "กราฟรอบเอว", en: "Waist chart", zh: "腰围图" },
  "wallet.reduced": { th: "ลดไปแล้ว {x} ซม.", en: "Reduced {x} cm", zh: "已减少 {x} 厘米" },
  "wallet.noWaist": { th: "ยังไม่มีการวัดรอบเอว", en: "No waist measurements yet", zh: "暂无腰围记录" },
  "wallet.photos": { th: "รูป before/after (เห็นเฉพาะคุณ)", en: "Before/after photos (only you can see)", zh: "前后对比照（仅您可见）" },
  "wallet.before": { th: "ก่อน", en: "Before", zh: "之前" },
  "wallet.after": { th: "หลัง", en: "After", zh: "之后" },

  // ── Gift Card ──
  "gift.title": { th: "Gift Card สบายใจ สปา", en: "Sabai Jai Gift Card", zh: "舒心水疗礼品卡" },
  "gift.buy": { th: "ซื้อ Gift Card", en: "Buy a gift card", zh: "购买礼品卡" },
  "gift.value": { th: "มูลค่า (฿500–฿10,000)", en: "Value (฿500–฿10,000)", zh: "面值（500–10,000 泰铢）" },
  "gift.design": { th: "ลายบัตร", en: "Card design", zh: "卡面设计" },
  "design.orchid": { th: "กล้วยไม้", en: "Orchid", zh: "兰花" },
  "design.lotus": { th: "บัว", en: "Lotus", zh: "莲花" },
  "design.gold": { th: "ทอง", en: "Gold", zh: "金色" },
  "gift.channel": { th: "ส่งทาง", en: "Send via", zh: "发送方式" },
  "channel.line": { th: "LINE", en: "LINE", zh: "LINE" },
  "channel.email": { th: "อีเมล", en: "Email", zh: "电子邮件" },
  "gift.recipient": { th: "ผู้รับ (LINE ID หรืออีเมล)", en: "Recipient (LINE ID or email)", zh: "收件人（LINE ID 或邮箱）" },
  "gift.message": { th: "ข้อความถึงผู้รับ", en: "Message", zh: "留言" },
  "gift.submit": { th: "ซื้อและส่งบัตร", en: "Buy and send", zh: "购买并发送" },
  "gift.sent": { th: "ส่งบัตรทาง {channel} ถึง {to} แล้ว (จำลอง — ไม่ได้ส่งจริง)", en: "Card sent via {channel} to {to} (simulated — not actually sent)", zh: "已通过 {channel} 发送给 {to}（模拟，未实际发送）" },
  "gift.preview": { th: "ข้อความที่ส่ง", en: "Message sent", zh: "发送内容" },
  "gift.previewText": { th: "คุณได้รับ Gift Card สบายใจ สปา มูลค่า {v} รหัส {code} ใช้ได้ถึง {d}", en: "You received a Sabai Jai Spa gift card worth {v}, code {code}, valid until {d}", zh: "您收到舒心水疗礼品卡，面值 {v}，卡号 {code}，有效期至 {d}" },
  "gift.expires": { th: "ใช้ได้ถึง {d}", en: "Valid until {d}", zh: "有效期至 {d}" },
  "gift.code": { th: "รหัสบัตร", en: "Card code", zh: "卡号" },
  "gift.check": { th: "ตรวจยอด Gift Card", en: "Check gift card balance", zh: "查询礼品卡余额" },
  "gift.checkBtn": { th: "ตรวจยอด", en: "Check", zh: "查询" },
  "gift.balance": { th: "ยอดคงเหลือ {b}", en: "Balance {b}", zh: "余额 {b}" },
  "gift.ok": { th: "ใช้ได้", en: "Valid", zh: "可用" },

  // ── รถรับส่ง ──
  "transport.title": { th: "รถรับส่งโรงแรม", en: "Hotel shuttle", zh: "酒店接送" },
  "transport.rule": { th: "≤ 5 กม. ฟรี · มากกว่า 5 ถึง 15 กม. ฿300 ต่อคัน · คันละไม่เกิน 4 คน · เกิน 15 กม. ไม่รับ", en: "≤ 5 km free · over 5 up to 15 km ฿300 per vehicle · max 4 people per vehicle · over 15 km not served", zh: "≤5公里免费 · 5–15公里每车 300 泰铢 · 每车最多4人 · 超过15公里不接送" },
  "transport.calc": { th: "คำนวณค่ารถ", en: "Calculate", zh: "计算" },
  "transport.fee": { th: "ค่ารถ {f}", en: "Shuttle fee {f}", zh: "接送费 {f}" },
  "transport.vehicles": { th: "{v} คัน", en: "{v} vehicle(s)", zh: "{v} 辆" },

  // ── แชท ──
  "chat.title": { th: "ผู้ช่วยแชท", en: "Chat assistant", zh: "聊天助手" },
  "chat.placeholder": { th: "พิมพ์คำถาม เช่น ร้านเปิดกี่โมง / นวดไทยราคาเท่าไหร่ / จองคิว", en: "Ask e.g. opening hours / Thai massage price / book", zh: "例如：营业时间 / 泰式按摩多少钱 / 预约" },
  "chat.send": { th: "ส่ง", en: "Send", zh: "发送" },
  "chat.input": { th: "ข้อความถึงผู้ช่วย", en: "Message to assistant", zh: "发给助手的消息" },

  // ── แบบทดสอบ ──
  "quiz.title": { th: "แบบทดสอบ 4 ข้อ หาแพ็กเกจที่ใช่", en: "4-question quiz to find your package", zh: "4题测试找到适合你的套餐" },
  "quiz.progress": { th: "ข้อ {n}/4", en: "Question {n}/4", zh: "第 {n}/4 题" },
  "quiz.result": { th: "แพ็กเกจที่แนะนำ", en: "Recommended package", zh: "推荐套餐" },
  "quiz.reason": { th: "เหตุผล", en: "Why", zh: "原因" },
  "quiz.restart": { th: "ทำใหม่", en: "Start over", zh: "重新开始" },

  // ── วิเคราะห์ผิว ──
  "skin.title": { th: "วิเคราะห์ผิวจากเซลฟี่", en: "Selfie skin analysis", zh: "自拍肌肤分析" },
  "skin.notice": { th: "รูปของคุณจะถูกวิเคราะห์ในเครื่องนี้เท่านั้น ไม่ถูกส่งออกหรือเก็บไว้ และหายไปเมื่อปิดหรือรีเฟรชหน้า", en: "Your photo is analysed on this device only. It is never uploaded or stored and disappears when you close or refresh the page.", zh: "照片仅在本设备上分析，不会上传或保存，关闭或刷新页面后即消失。" },
  "skin.accept": { th: "รับทราบ เลือกรูป", en: "I understand, choose a photo", zh: "我已了解，选择照片" },
  "skin.choose": { th: "เลือกรูปเซลฟี่", en: "Choose a selfie", zh: "选择自拍照" },
  "skin.sample": { th: "ใช้ภาพตัวอย่างของร้าน", en: "Use shop sample image", zh: "使用店内示例图" },
  "skin.result": { th: "ผลวิเคราะห์", en: "Result", zh: "分析结果" },
  "skin.recommend": { th: "ทรีตเมนต์แนะนำ", en: "Recommended treatments", zh: "推荐护理" },
  "skin.sim": { th: "ภาพจำลองก่อน/หลัง", en: "Before/after simulation", zh: "前后效果模拟" },
  "skin.simLabel": { th: "ภาพจำลอง ผลจริงแต่ละคนต่างกัน", en: "Simulation only — actual results vary by person", zh: "仅为模拟效果，实际效果因人而异" },
  "skin.before": { th: "ก่อน", en: "Before", zh: "之前" },
  "skin.after": { th: "หลัง (จำลอง)", en: "After (simulated)", zh: "之后（模拟）" },
  "skin.type.oily": { th: "ผิวมันและหมองคล้ำเล็กน้อย", en: "Oily, slightly dull skin", zh: "偏油、略暗沉" },
  "skin.type.red": { th: "ผิวแดงระคายเคืองง่าย", en: "Redness-prone, sensitive skin", zh: "易泛红、敏感" },
  "skin.type.dry": { th: "ผิวแห้งขาดความชุ่มชื้น", en: "Dry, dehydrated skin", zh: "干燥缺水" },
  "skin.type.balanced": { th: "ผิวค่อนข้างสมดุล", en: "Fairly balanced skin", zh: "肤质较平衡" },
  "skin.metrics": { th: "ความสว่าง {b} · ความแดง {r} · ความสม่ำเสมอ {u}", en: "Brightness {b} · Redness {r} · Evenness {u}", zh: "亮度 {b} · 泛红 {r} · 均匀度 {u}" },

  // ── เข้าสู่ระบบ ──
  "login.title": { th: "เข้าสู่ระบบ", en: "Log in", zh: "登录" },
  "login.email": { th: "อีเมล", en: "Email", zh: "邮箱" },
  "login.password": { th: "รหัสผ่าน", en: "Password", zh: "密码" },
  "login.submit": { th: "เข้าสู่ระบบ", en: "Log in", zh: "登录" },

  // ── หลังร้าน ──
  "admin.title": { th: "หลังร้าน · ตารางคิว", en: "Back office · Queue", zh: "后台 · 预约表" },
  "admin.date": { th: "วันที่", en: "Date", zh: "日期" },
  "admin.show": { th: "แสดง", en: "Show", zh: "显示" },
  "admin.complete": { th: "ใช้บริการเสร็จ", en: "Mark completed", zh: "服务完成" },
  "admin.waist": { th: "รอบเอว (ซม.)", en: "Waist (cm)", zh: "腰围（厘米）" },
  "admin.none": { th: "ไม่มีคิวในวันนี้", en: "No bookings on this date", zh: "当天没有预约" },
  "admin.reset": { th: "รีเซ็ตข้อมูลทดสอบ", en: "Reset test data", zh: "重置测试数据" },
  "admin.resetDone": { th: "รีเซ็ตแล้ว", en: "Reset done", zh: "已重置" },
  "admin.done": { th: "บันทึกแล้ว · แต้ม +{p}", en: "Saved · +{p} points", zh: "已保存 · +{p} 积分" },
  "admin.customer": { th: "ลูกค้า", en: "Customer", zh: "客户" },
  "admin.time": { th: "เวลา", en: "Time", zh: "时间" },
  "admin.status": { th: "สถานะ", en: "Status", zh: "状态" },
  "admin.action": { th: "จัดการ", en: "Action", zh: "操作" },
  "admin.today": { th: "วันนี้ของระบบ: {d}", en: "System today: {d}", zh: "系统今天：{d}" },

  // ── CR-05 รายงานยอด ──
  "report.title": { th: "รายงานยอด", en: "Sales report", zh: "销售报表" },
  "report.hint": { th: "นับตามวันนัด (เวลาไทย) รวมวันแรกและวันสุดท้าย · ไม่เกิน 92 วันต่อครั้ง", en: "Counted by appointment date (Bangkok time), first and last day included · up to 92 days at a time", zh: "按预约日期（曼谷时间）统计，含首尾两天 · 每次最多92天" },
  "report.from": { th: "ตั้งแต่วันที่", en: "From", zh: "开始日期" },
  "report.to": { th: "ถึงวันที่", en: "To", zh: "结束日期" },
  "report.run": { th: "ดูรายงาน", en: "Show report", zh: "查看报表" },
  "report.csv": { th: "โหลดไฟล์ Excel (CSV)", en: "Download Excel file (CSV)", zh: "下载Excel文件（CSV）" },
  "report.counts": { th: "จำนวนนัด", en: "Appointments", zh: "预约数量" },
  "report.money": { th: "ยอดขาย (นัดที่ใช้บริการแล้ว)", en: "Sales (completed appointments)", zh: "销售额（已完成预约）" },
  "report.revenue": { th: "ยอดขายรวม", en: "Total sales", zh: "销售总额" },
  "report.giftcardPaid": { th: "จ่ายด้วยบัตรของขวัญ", en: "Paid by gift card", zh: "礼品卡支付" },
  "report.otherPaid": { th: "จ่ายช่องทางอื่น", en: "Paid by other methods", zh: "其他方式支付" },
  "report.transportFee": { th: "ค่ารถ (รวมอยู่ในยอดขาย)", en: "Transport fee (included in sales)", zh: "车费（已含在销售额中）" },
  "report.discGroup": { th: "ส่วนลดกลุ่ม", en: "Group discount", zh: "团体折扣" },
  "report.discTier": { th: "ส่วนลดระดับสมาชิก", en: "Member tier discount", zh: "会员等级折扣" },
  "report.discBirthday": { th: "ส่วนลดเดือนเกิด", en: "Birthday discount", zh: "生日月折扣" },
  "report.other": { th: "แต้มและคอร์ส", en: "Points and courses", zh: "积分与疗程" },
  "report.points": { th: "แต้มที่ให้ลูกค้า", en: "Points given", zh: "发放积分" },
  "report.course": { th: "ครั้งคอร์สที่ใช้", en: "Course sessions used", zh: "已用疗程次数" },
  "report.pending": { th: "ยอดของนัดที่ยังไม่มา (สถานะยืนยัน)", en: "Value of upcoming appointments (confirmed)", zh: "未到店预约金额（已确认）" },
  "report.byTherapist": { th: "คิวที่ใช้บริการแล้วต่อนักบำบัด", en: "Completed appointments per therapist", zh: "每位理疗师完成的预约" },
  "report.queues": { th: "คิว", en: "Appointments", zh: "预约" },
  "report.item": { th: "รายการ", en: "Item", zh: "项目" },
  "report.value": { th: "ค่า", en: "Value", zh: "数值" },

  // ── ข้อความ error (API ตอบ code + message ภาษาเดียวกับ cookie lang) ──
  "err.SLOT_TAKEN": { th: "เวลานี้ถูกจองแล้ว", en: "This time is already booked", zh: "该时段已被预订" },
  // BR-21 (CR-03) · {code} = รหัสนัดเดิม (extra.existing)
  "err.DUPLICATE_BOOKING": { th: "คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส {code})", en: "You already have a booking at this time (code {code})", zh: "您在该时段已有预约（预约号 {code}）" },
  "err.GROUP_CALL_SHOP": { th: "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน", en: "Groups of 7 or more, please call the shop", zh: "7人及以上团体请致电本店" },
  "err.OUT_OF_AREA": { th: "อยู่นอกพื้นที่รับส่ง", en: "Outside the pickup area", zh: "超出接送范围" },
  "err.GC_EXPIRED": { th: "บัตรหมดอายุแล้ว", en: "This card has expired", zh: "此卡已过期" },
  "err.GC_EMPTY": { th: "บัตรนี้ไม่มียอดคงเหลือ", en: "This card has no balance left", zh: "此卡余额为零" },
  "err.GC_NOT_FOUND": { th: "ไม่พบ Gift Card นี้", en: "Gift card not found", zh: "未找到该礼品卡" },
  "err.GC_VALUE": { th: "มูลค่าต้องเป็นจำนวนเต็ม ฿500–฿10,000", en: "Value must be a whole number from ฿500 to ฿10,000", zh: "面值须为 500–10,000 泰铢的整数" },
  "err.GC_FIELDS": { th: "กรุณาเลือกลาย ช่องทาง และกรอกผู้รับ", en: "Please choose a design, channel and recipient", zh: "请选择卡面、发送方式并填写收件人" },
  "err.DATE_OUT_OF_RANGE": { th: "เลือกวันได้ตั้งแต่พรุ่งนี้ถึงอีก 30 วัน", en: "Choose a date from tomorrow up to 30 days ahead", zh: "只能选择明天起30天内的日期" },
  // CR-04 วันหยุดร้าน · {name} = ชื่อวันหยุดตามภาษา (extra.name)
  "err.SHOP_CLOSED": { th: "วันนี้ร้านหยุด ({name}) กรุณาเลือกวันอื่น", en: "The shop is closed on this day ({name}). Please choose another date", zh: "本店当天休息（{name}），请选择其他日期" },
  "err.SLOT_INVALID": { th: "ไม่มีรอบเวลานี้", en: "This time slot does not exist", zh: "没有这个时段" },
  "err.SINGLE_ONE": { th: "จองเดี่ยวได้ 1 คน", en: "Single booking is for 1 person", zh: "单人预约限1人" },
  "err.COUPLE_NEEDS_2": { th: "จองคู่ต้องมี 2 คนพอดี (3 คนขึ้นไปให้จองกลุ่ม)", en: "Couple booking needs exactly 2 people (3+ please book a group)", zh: "双人预约须为2人（3人以上请团体预约）" },
  "err.GROUP_TOO_SMALL": { th: "จองกลุ่มต้องมี 3–6 คน (1–2 คนให้จองเดี่ยวหรือคู่)", en: "Group booking needs 3–6 people (1–2 please book single or couple)", zh: "团体预约需3–6人（1–2人请单人或双人预约）" },
  "err.BAD_PEOPLE": { th: "จำนวนคนไม่ถูกต้อง", en: "Invalid number of people", zh: "人数无效" },
  "err.THERAPIST_INVALID": { th: "นักบำบัดที่เลือกทำบริการนี้ไม่ได้", en: "The selected therapist does not offer this service", zh: "所选理疗师不提供此服务" },
  "err.SERVICE_INVALID": { th: "ไม่พบบริการนี้ หรือแบบการจองไม่ตรงกับบริการ", en: "Service not found or does not match the booking type", zh: "未找到服务或与预约类型不符" },
  "err.PRICE_CHANGED": { th: "ราคาเปลี่ยน กรุณาตรวจสอบสรุปอีกครั้ง", en: "The price has changed, please review the summary again", zh: "价格已变更，请重新确认汇总" },
  "err.CANCEL_TOO_LATE": { th: "เหลือเวลาน้อยกว่า 24 ชม. ยกเลิกเองไม่ได้ กรุณาโทรหาร้าน", en: "Less than 24 hours left — please call the shop to cancel", zh: "距离预约不足24小时，无法自行取消，请致电本店" },
  "err.RESCHEDULE_TOO_LATE": { th: "เลื่อนนัดเองได้เมื่อเหลือเวลาก่อนนัดอย่างน้อย 24 ชั่วโมง กรุณาโทร {phone}", en: "You can reschedule up to 24 hours before your appointment. Please call {phone}", zh: "距预约不足24小时，无法自行改期，请致电 {phone}" },
  "err.RESCHEDULE_NOT_ALLOWED": { th: "นัดนี้เลื่อนไม่ได้", en: "This booking cannot be rescheduled", zh: "该预约无法改期" },
  "err.RESCHEDULE_BIRTHDAY": { th: "นัดที่ใช้ส่วนลดเดือนเกิดเลื่อนได้ภายในเดือนเกิดเท่านั้น", en: "Birthday-discount bookings can only move within your birthday month", zh: "生日优惠预约只能在生日当月内改期" },
  "err.RESCHEDULE_SAME": { th: "วันและเวลาใหม่ต้องไม่ตรงกับนัดเดิม", en: "The new date and time must differ from the current booking", zh: "新的日期和时间不能与原预约相同" },
  "err.CANCEL_NOT_ALLOWED": { th: "นัดนี้ยกเลิกไม่ได้", en: "This appointment cannot be cancelled", zh: "此预约无法取消" },
  "err.COURSE_UNAVAILABLE": { th: "ใช้คอร์สนี้ไม่ได้ (เหลือ 0 ครั้งหรือหมดอายุ)", en: "This course cannot be used (0 sessions left or expired)", zh: "此疗程无法使用（剩余0次或已过期）" },
  "err.POINTS_NOT_ENOUGH": { th: "แต้มไม่พอแลก", en: "Not enough points", zh: "积分不足" },
  "err.BIRTHDAY_UNAVAILABLE": { th: "ใช้ส่วนลดเดือนเกิดไม่ได้", en: "Birthday discount is not available", zh: "无法使用生日折扣" },
  "err.CONTACT_REQUIRED": { th: "กรุณากรอกชื่อและเบอร์โทร", en: "Please enter your name and phone", zh: "请填写姓名和电话" },
  "err.QUOTE_REQUIRED": { th: "ต้องส่งยอดที่แสดงในหน้าสรุป (quotedTotal)", en: "quotedTotal from the summary is required", zh: "需要提供汇总金额 quotedTotal" },
  "err.BAD_DISTANCE": { th: "ระยะทางไม่ถูกต้อง", en: "Invalid distance", zh: "距离无效" },
  "err.BAD_REQUEST": { th: "ข้อมูลไม่ถูกต้อง", en: "Invalid request", zh: "请求无效" },
  "err.LOGIN_REQUIRED": { th: "กรุณาเข้าสู่ระบบ", en: "Please log in", zh: "请登录" },
  "err.LOGIN_FAILED": { th: "อีเมลหรือรหัสผ่านไม่ถูกต้อง", en: "Incorrect email or password", zh: "邮箱或密码错误" },
  "err.FORBIDDEN": { th: "ไม่มีสิทธิ์เข้าถึง", en: "Access denied", zh: "无权访问" },
  "err.REPORT_RANGE": { th: "เลือกช่วงวันได้ไม่เกิน 92 วัน และวันเริ่มต้องไม่เกินวันสิ้นสุด", en: "Choose a range of at most 92 days, with the start date not after the end date", zh: "日期范围最多92天，且开始日期不能晚于结束日期" }, // CR-05
  "err.NOT_FOUND": { th: "ไม่พบข้อมูล", en: "Not found", zh: "未找到" },
  "err.NOT_CONFIRMED": { th: "นัดนี้ไม่ได้อยู่ในสถานะยืนยัน", en: "This appointment is not confirmed", zh: "此预约不是已确认状态" },
  "err.SERVER": { th: "ระบบขัดข้อง กรุณาลองใหม่", en: "Something went wrong, please try again", zh: "系统错误，请重试" },
} satisfies Record<string, Entry>;

export type Key = keyof typeof D;

export function t(lang: Lang, key: Key | string, vars?: Record<string, string | number>): string {
  const e = (D as Record<string, Entry>)[key];
  let s = e ? e[lang] : key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

export function hasKey(key: string): boolean {
  return key in D;
}

/** ชื่อในภาษาที่เลือกจากแถว db (name_th/name_en/name_zh หรือ name/name_en/name_zh) */
export function pickName(r: object, lang: Lang): string {
  const row = r as Record<string, unknown>;
  if (lang === "en") return String(row.name_en ?? row.name_th ?? row.name);
  if (lang === "zh") return String(row.name_zh ?? row.name_th ?? row.name);
  return String(row.name_th ?? row.name);
}

/** วันที่ YYYY-MM-DD → แสดงตามภาษา (ไทยใช้ พ.ศ. ไม่ได้ใช้เพื่อให้ตรง TEST-DATA: แสดง ค.ศ.) */
const TH_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
const EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export function formatDate(date: string, lang: Lang): string {
  const [y, m, d] = date.split("-").map(Number);
  if (lang === "en") return `${d} ${EN_MONTHS[m - 1]} ${y}`;
  if (lang === "zh") return `${y}年${m}月${d}日`;
  return `${d} ${TH_MONTHS[m - 1]} ${y}`;
}

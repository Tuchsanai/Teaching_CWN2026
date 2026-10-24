// ค่าตั้งของระบบที่อ่านจาก env จุดเดียว
export const config = {
  /** เปิด /api/test/*, นาฬิกาทดสอบ, บัญชีทดสอบหน้า login, ปุ่มรีเซ็ต /admin */
  get allowTestReset(): boolean {
    return (process.env.ALLOW_TEST_RESET ?? "1") === "1";
  },
};

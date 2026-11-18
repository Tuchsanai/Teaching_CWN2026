'use client';
// ปุ่มเปิดแชทน้องช่างจากที่ไหนก็ได้ (ChatWidget ฟัง event 'bm:chat-open')
export default function OpenChatButton({ children, className = 'btn', voice = false }: { children: React.ReactNode; className?: string; voice?: boolean }) {
  return (
    <button type="button" className={className} onClick={() => window.dispatchEvent(new CustomEvent('bm:chat-open', { detail: { voice } }))}>
      {children}
    </button>
  );
}

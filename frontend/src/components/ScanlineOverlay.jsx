import { useEffect, useState } from "react";

export default function ScanlineOverlay() {
  const [show, setShow] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShow(false), 900);
    return () => clearTimeout(timer);
  }, []);

  if (!show) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-40 overflow-hidden">
      <div className="absolute left-0 right-0 h-px bg-amber shadow-[0_0_12px_2px_rgba(232,163,61,0.6)] animate-scanline" />
    </div>
  );
}
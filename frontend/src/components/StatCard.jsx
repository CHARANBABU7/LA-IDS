import { useCountUp } from "../hooks/useCountUp";

export default function StatCard({ label, value, accent = "amber", icon: Icon }) {
  const accentColor = accent === "rust" ? "text-rust" : "text-amber";
  const animatedValue = useCountUp(typeof value === "number" ? value : 0);

  return (
    <div className="bg-panel/50 border border-panel rounded-lg p-5 flex items-start justify-between hover:border-amber/30 transition-colors duration-300">
      <div>
        <p className="text-xs uppercase tracking-wide text-slate/50 font-mono mb-2">{label}</p>
        <p className={`text-3xl font-display font-semibold ${accentColor} tabular-nums`}>
          {typeof value === "number" ? animatedValue : value}
        </p>
      </div>
      {Icon && <Icon size={20} className={`${accentColor} opacity-60`} />}
    </div>
  );
}
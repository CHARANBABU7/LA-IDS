export default function StatCard({ label, value, accent = "amber", icon: Icon }) {
  const accentColor = accent === "rust" ? "text-rust" : "text-amber";

  return (
    <div className="bg-panel/50 border border-panel rounded-lg p-5 flex items-start justify-between">
      <div>
        <p className="text-xs uppercase tracking-wide text-slate/50 font-mono mb-2">{label}</p>
        <p className={`text-3xl font-display font-semibold ${accentColor}`}>{value}</p>
      </div>
      {Icon && <Icon size={20} className={`${accentColor} opacity-60`} />}
    </div>
  );
}
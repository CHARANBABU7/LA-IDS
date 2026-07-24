const styles = {
  low: "bg-slate/10 text-slate border-slate/30",
  medium: "bg-amber/10 text-amber border-amber/30",
  high: "bg-rust/10 text-rust border-rust/30",
};

export default function SeverityBadge({ severity }) {
  const style = styles[severity] || styles.low;
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-mono uppercase border ${style}`}>
      {severity}
    </span>
  );
}
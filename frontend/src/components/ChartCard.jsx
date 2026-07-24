export default function ChartCard({ title, children }) {
  return (
    <div className="bg-panel/50 border border-panel rounded-lg p-5">
      <h2 className="font-display text-sm text-bone mb-4">{title}</h2>
      {children}
    </div>
  );
}
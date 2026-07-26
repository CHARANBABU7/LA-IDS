import { MapPin, Clock } from "lucide-react";
import SeverityBadge from "./SeverityBadge";

const statusStyles = {
  open: "text-rust",
  investigating: "text-amber",
  resolved: "text-slate/50",
  false_positive: "text-slate/30",
};

export default function AlertCard({ alert, onClick }) {
  return (
    <div
  onClick={onClick}
   tabIndex={0}
  role="button"
  onKeyDown={(e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    onClick();
  }
}}
className={`bg-panel/50 border rounded-lg p-4 cursor-pointer hover:border-amber/40 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber ${
      alert.severity === "high" && alert.status === "open"
      ? "border-rust/40 shadow-[0_0_0_1px_rgba(193,68,14,0.15)]"
      : "border-panel"
  }`}
>
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-display text-sm text-bone">{alert.attack_type.replace(/_/g, " ")}</p>
          <p className="text-xs text-slate/50 font-mono mt-1">{alert.description}</p>
        </div>
        <SeverityBadge severity={alert.severity} />
      </div>
      <div className="flex items-center gap-4 text-xs font-mono text-slate/50">
        <span className="flex items-center gap-1"><MapPin size={12} /> {alert.source_ip}</span>
        <span className="flex items-center gap-1"><Clock size={12} /> {new Date(alert.timestamp).toLocaleString()}</span>
        <span className={`ml-auto uppercase ${statusStyles[alert.status] || ""}`}>{alert.status.replace(/_/g, " ")}</span>
      </div>
      
    </div>
    
  );
}
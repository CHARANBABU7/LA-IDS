import { X } from "lucide-react";
import SeverityBadge from "./SeverityBadge";

const STATUS_OPTIONS = ["open", "investigating", "resolved", "false_positive"];

export default function AlertDetailModal({ alert, onClose, onStatusChange }) {
  if (!alert) return null;

  return (
    <div className="fixed inset-0 bg-void/80 flex items-center justify-center z-50 p-6" onClick={onClose}>
      <div
        className="bg-panel border border-panel rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="font-display text-lg text-bone">{alert.attack_type.replace(/_/g, " ")}</h2>
            <p className="text-xs text-slate/50 font-mono mt-1">{alert.source_ip}</p>
          </div>
          <button onClick={onClose} className="text-slate/50 hover:text-bone">
            <X size={20} />
          </button>
        </div>

        <div className="flex items-center gap-3 mb-4">
          <SeverityBadge severity={alert.severity} />
          <select
            value={alert.status}
            onChange={(e) => onStatusChange(alert.id, e.target.value)}
            className="bg-void border border-panel rounded px-2 py-1 text-xs font-mono text-bone focus:outline-none focus:border-amber/50"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
            ))}
          </select>
        </div>

        <div className="space-y-4 text-sm">
          <div>
            <p className="text-xs uppercase text-slate/40 font-mono mb-1">Detection Explanation</p>
            <p className="text-slate">{alert.description}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate/40 font-mono mb-1">Recommendation</p>
            <p className="text-slate">{alert.recommendation}</p>
          </div>

          {alert.related_logs && (
            <div>
              <p className="text-xs uppercase text-slate/40 font-mono mb-2">
                Evidence ({alert.related_logs.length} log{alert.related_logs.length !== 1 ? "s" : ""})
              </p>
              <div className="space-y-1 max-h-56 overflow-y-auto">
                {alert.related_logs.map((log) => (
                  <p key={log.id} className="font-mono text-xs text-slate/60 bg-void/60 rounded px-2 py-1.5 truncate">
                    {log.raw_log}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
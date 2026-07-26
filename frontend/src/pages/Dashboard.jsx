import { useEffect, useState } from "react";
import { FileText, ShieldAlert, AlertTriangle, ShieldCheck } from "lucide-react";
import { getDashboardSummary } from "../api/dashboard";
import StatCard from "../components/StatCard";
import SeverityBadge from "../components/SeverityBadge";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
  const load = () => getDashboardSummary().then(setData).catch(() => setError("Could not reach the backend."));
  load();
  const interval = setInterval(load, 15000); // refresh every 15s
  return () => clearInterval(interval);
}, []);
  if (error) {
    return (
      <div className="text-rust font-mono text-sm border border-rust/30 bg-rust/10 rounded-lg p-4">
        {error}
      </div>
    );
  }

  if (!data) {
    return <p className="text-slate/50 font-mono text-sm">Loading dashboard...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-semibold text-bone">Dashboard</h1>
        <p className="text-sm text-slate/50 mt-1">
          {data.open_alerts} open alert{data.open_alerts !== 1 ? "s" : ""} across {data.total_logs} ingested logs.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Logs" value={data.total_logs} icon={FileText} />
        <StatCard label="Total Alerts" value={data.total_alerts} icon={ShieldAlert} />
        <StatCard label="Open Alerts" value={data.open_alerts} icon={AlertTriangle} accent="rust" />
        <StatCard label="Resolved" value={data.resolved_alerts} icon={ShieldCheck} />
      </div>

<div className="grid grid-cols-1 md:grid-cols-2 gap-4">        {/* Attack Type Breakdown */}
        <div className="bg-panel/50 border border-panel rounded-lg p-5">
          <h2 className="font-display text-sm text-bone mb-4">Attack Types</h2>
          <div className="space-y-2">
            {data.attack_type_breakdown.length === 0 && (
              <p className="text-slate/40 text-sm font-mono">No attacks detected yet.</p>
            )}
            {data.attack_type_breakdown.map((item) => (
              <div key={item.attack_type} className="flex items-center justify-between text-sm">
                <span className="font-mono text-slate">{item.attack_type.replace(/_/g, " ")}</span>
                <span className="text-amber font-mono">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Attackers */}
        <div className="bg-panel/50 border border-panel rounded-lg p-5">
          <h2 className="font-display text-sm text-bone mb-4">Top Attacking IPs</h2>
          <div className="space-y-2">
            {data.top_attackers.length === 0 && (
              <p className="text-slate/40 text-sm font-mono">No attackers identified yet.</p>
            )}
            {data.top_attackers.map((attacker) => (
              <div key={attacker.source_ip} className="flex items-center justify-between text-sm">
                <span className="font-mono text-slate">{attacker.source_ip}</span>
                <span className="text-amber font-mono">{attacker.alert_count} alert{attacker.alert_count !== 1 ? "s" : ""}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Severity Breakdown */}
      <div className="bg-panel/50 border border-panel rounded-lg p-5">
        <h2 className="font-display text-sm text-bone mb-4">Open Alert Severity</h2>
        <div className="flex gap-6">
          <div className="flex items-center gap-2">
            <SeverityBadge severity="low" /> <span className="text-sm font-mono">{data.severity_breakdown.low}</span>
          </div>
          <div className="flex items-center gap-2">
            <SeverityBadge severity="medium" /> <span className="text-sm font-mono">{data.severity_breakdown.medium}</span>
          </div>
          <div className="flex items-center gap-2">
            <SeverityBadge severity="high" /> <span className="text-sm font-mono">{data.severity_breakdown.high}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
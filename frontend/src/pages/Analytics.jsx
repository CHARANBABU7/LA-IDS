import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line,
} from "recharts";
import { getDashboardSummary } from "../api/dashboard";
import { getLogs } from "../api/logs";
import ChartCard from "../components/ChartCard";

const SEVERITY_COLORS = { low: "#C9C4D1", medium: "#E8A33D", high: "#C1440E" };
const ATTACK_COLORS = ["#E8A33D", "#C1440E", "#C9C4D1", "#8A6D3B", "#5C4A2A"];

const tooltipStyle = {
  backgroundColor: "#1A1720",
  border: "1px solid #2A2630",
  borderRadius: "6px",
  fontFamily: "IBM Plex Mono, monospace",
  fontSize: "12px",
  color: "#F2EFEA",
};

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getDashboardSummary(), getLogs()])
      .then(([summaryData, logsData]) => {
        setSummary(summaryData);
        setLogs(logsData);
      })
      .catch(() => setError("Could not reach the backend."));
  }, []);

  if (error) {
    return <div className="text-rust font-mono text-sm border border-rust/30 bg-rust/10 rounded-lg p-4">{error}</div>;
  }
  if (!summary) {
    return <p className="text-slate/50 font-mono text-sm">Loading analytics...</p>;
  }

  const severityData = [
    { name: "Low", value: summary.severity_breakdown.low, color: SEVERITY_COLORS.low },
    { name: "Medium", value: summary.severity_breakdown.medium, color: SEVERITY_COLORS.medium },
    { name: "High", value: summary.severity_breakdown.high, color: SEVERITY_COLORS.high },
  ].filter((d) => d.value > 0);

  const attackTypeData = summary.attack_type_breakdown.map((item) => ({
    name: item.attack_type.replace(/_/g, " "),
    count: item.count,
  }));

  // Group logs by date for a simple events-over-time view
  const eventsByDate = {};
  logs.forEach((log) => {
    if (!log.timestamp) return;
    const day = log.timestamp.split("T")[0];
    eventsByDate[day] = (eventsByDate[day] || 0) + 1;
  });
  const timeSeriesData = Object.entries(eventsByDate)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date, count }));

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-display font-semibold text-bone">Analytics</h1>
        <p className="text-sm text-slate/50 mt-1">Trends and breakdowns across all detected activity.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ChartCard title="Severity Distribution">
          {severityData.length === 0 ? (
            <p className="text-slate/40 font-mono text-sm py-12 text-center">No alerts yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={severityData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={3}>
                  {severityData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Attack Categories">
          {attackTypeData.length === 0 ? (
            <p className="text-slate/40 font-mono text-sm py-12 text-center">No attacks detected yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={attackTypeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2630" />
                <XAxis dataKey="name" tick={{ fill: "#C9C4D1", fontSize: 10, fontFamily: "IBM Plex Mono" }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis tick={{ fill: "#C9C4D1", fontSize: 10, fontFamily: "IBM Plex Mono" }} allowDecimals={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "#2A263050" }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {attackTypeData.map((_, i) => <Cell key={i} fill={ATTACK_COLORS[i % ATTACK_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>

      <ChartCard title="Events Over Time">
        {timeSeriesData.length === 0 ? (
          <p className="text-slate/40 font-mono text-sm py-12 text-center">No log activity yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2630" />
              <XAxis dataKey="date" tick={{ fill: "#C9C4D1", fontSize: 10, fontFamily: "IBM Plex Mono" }} />
              <YAxis tick={{ fill: "#C9C4D1", fontSize: 10, fontFamily: "IBM Plex Mono" }} allowDecimals={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="count" stroke="#E8A33D" strokeWidth={2} dot={{ fill: "#E8A33D", r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </ChartCard>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ChartCard title="Top Source IPs">
          <div className="space-y-2">
            {summary.top_attackers.length === 0 && <p className="text-slate/40 text-sm font-mono">No data yet.</p>}
            {summary.top_attackers.map((a) => (
              <div key={a.source_ip} className="flex justify-between text-sm font-mono">
                <span className="text-slate">{a.source_ip}</span>
                <span className="text-amber">{a.alert_count}</span>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard title="Most Frequent Attack Type">
          {attackTypeData.length === 0 ? (
            <p className="text-slate/40 text-sm font-mono">No data yet.</p>
          ) : (
            <p className="text-2xl font-display text-amber">
              {[...attackTypeData].sort((a, b) => b.count - a.count)[0].name}
            </p>
          )}
        </ChartCard>
      </div>
    </div>
  );
}
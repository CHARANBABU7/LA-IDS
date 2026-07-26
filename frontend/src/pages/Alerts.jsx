import { useEffect, useState } from "react";
import { getAlerts, investigateAlert, updateAlertStatus } from "../api/alerts";
import AlertCard from "../components/AlertCard";
import AlertDetailModal from "../components/AlertDetailModal";

const SEVERITIES = ["", "low", "medium", "high"];
const STATUSES = ["", "open", "investigating", "resolved", "false_positive"];

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedAlert, setSelectedAlert] = useState(null);

  const fetchAlerts = () => {
    setLoading(true);
    getAlerts({ severity: severityFilter || undefined, status: statusFilter || undefined })
      .then((data) => {
        setAlerts(data);
        setError(null);
      })
      .catch(() => setError("Could not reach the backend."))
      .finally(() => setLoading(false));
  };
useEffect(() => {
  fetchAlerts();
  const interval = setInterval(fetchAlerts, 15000);
  return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [severityFilter, statusFilter]);

  const openAlertDetail = async (alertId) => {
    const detail = await investigateAlert(alertId);
    setSelectedAlert(detail);
  };

  const handleStatusChange = async (alertId, newStatus) => {
    await updateAlertStatus(alertId, newStatus);
    const refreshed = await investigateAlert(alertId);
    setSelectedAlert(refreshed);
    fetchAlerts();
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-display font-semibold text-bone">Alerts</h1>
        <p className="text-sm text-slate/50 mt-1">{alerts.length} alert{alerts.length !== 1 ? "s" : ""} matching current filters.</p>
      </div>

      <div className="flex gap-3">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-panel/50 border border-panel rounded-md px-3 py-2 text-sm font-mono text-bone focus:outline-none focus:border-amber/50"
        >
          {SEVERITIES.map((s) => <option key={s} value={s}>{s ? s : "all severities"}</option>)}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-panel/50 border border-panel rounded-md px-3 py-2 text-sm font-mono text-bone focus:outline-none focus:border-amber/50"
        >
          {STATUSES.map((s) => <option key={s} value={s}>{s ? s.replace(/_/g, " ") : "all statuses"}</option>)}
        </select>
      </div>

      {error && (
        <div className="text-rust font-mono text-sm border border-rust/30 bg-rust/10 rounded-lg p-4">{error}</div>
      )}

      {loading && !error && <p className="text-slate/50 font-mono text-sm">Loading alerts...</p>}

      {!loading && !error && (
<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.length === 0 && (
            <p className="text-slate/40 font-mono text-sm col-span-2 text-center py-8">No alerts match your filters.</p>
          )}
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onClick={() => openAlertDetail(alert.id)} />
          ))}
        </div>
      )}

      <AlertDetailModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
        onStatusChange={handleStatusChange}
      />
    </div>
  );
}
import { Fragment, useEffect, useState } from "react";
import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { getLogs } from "../api/logs";
import DataTable from "../components/DataTable";

export default function LogExplorer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [sourceIpFilter, setSourceIpFilter] = useState("");
  const [parsedOnly, setParsedOnly] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  const fetchLogs = () => {
    setLoading(true);
    getLogs({ sourceIp: sourceIpFilter || undefined, parsedOnly })
      .then((data) => {
        setLogs(data);
        setError(null);
      })
      .catch(() => setError("Could not reach the backend."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceIpFilter, parsedOnly]);

  const visibleLogs = logs.filter((log) => {
    if (!search) return true;
    const haystack = `${log.source_ip ?? ""} ${log.endpoint ?? ""} ${log.message ?? ""} ${log.username ?? ""}`.toLowerCase();
    return haystack.includes(search.toLowerCase());
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-display font-semibold text-bone">Log Explorer</h1>
        <p className="text-sm text-slate/50 mt-1">Browse and search all ingested log entries.</p>
      </div>

      {/* Search + Filters */}
      <div className="flex gap-3 items-center">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate/40" />
          <input
            type="text"
            placeholder="Search by IP, endpoint, message..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-panel/50 border border-panel rounded-md pl-9 pr-3 py-2 text-sm font-mono text-bone placeholder-slate/30 focus:outline-none focus:border-amber/50"
          />
        </div>

        <input
          type="text"
          placeholder="Filter by source IP"
          value={sourceIpFilter}
          onChange={(e) => setSourceIpFilter(e.target.value)}
          className="bg-panel/50 border border-panel rounded-md px-3 py-2 text-sm font-mono text-bone placeholder-slate/30 focus:outline-none focus:border-amber/50 w-56"
        />

        <label className="flex items-center gap-2 text-sm text-slate/60 font-mono whitespace-nowrap">
          <input
            type="checkbox"
            checked={parsedOnly}
            onChange={(e) => setParsedOnly(e.target.checked)}
            className="accent-amber"
          />
          parsed only
        </label>
      </div>

      {error && (
        <div className="text-rust font-mono text-sm border border-rust/30 bg-rust/10 rounded-lg p-4">
          {error}
        </div>
      )}

      {loading && !error && (
        <p className="text-slate/50 font-mono text-sm">Loading logs...</p>
      )}

      {!loading && !error && (
        <div className="overflow-x-auto">
        <DataTable
          columns={["Timestamp", "Source IP", "Method", "Endpoint / Message", "Status", ""]}
          emptyMessage="No logs match your filters."
        >
          {visibleLogs.map((log) => (
            <Fragment key={log.id}>
              <tr
                key={log.id}
            
                onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                className="hover:bg-panel/40 cursor-pointer transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber"
              >
                <td className="px-4 py-3 font-mono text-xs text-slate/60">
                  {log.timestamp ? new Date(log.timestamp).toLocaleString() : "—"}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-bone">{log.source_ip || "—"}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate/70">{log.request_method || "—"}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate/70 max-w-md truncate">
                  {log.endpoint || log.message}
                </td>
                <td className="px-4 py-3 font-mono text-xs">
                  {log.status_code ? (
                    <span className={log.status_code >= 400 ? "text-rust" : "text-amber"}>
                      {log.status_code}
                    </span>
                  ) : (
                    <span className="text-slate/30">unparsed</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
  <button
    type="button"
    aria-label={expandedId === log.id ? "Collapse log details" : "Expand log details"}
    aria-expanded={expandedId === log.id}
    onClick={(e) => {
      e.stopPropagation();
      setExpandedId(expandedId === log.id ? null : log.id);
    }}
    className="inline-flex items-center justify-center rounded-md p-1.5 text-slate/50 hover:bg-panel hover:text-amber transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber"
  >
    {expandedId === log.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
  </button>
</td>
              </tr>
              {expandedId === log.id && (
                <tr className="bg-void/60">
                  <td colSpan={6} className="px-4 py-3 font-mono text-xs text-slate/50">
                    <span className="text-slate/30">raw:</span> {log.raw_log}
                  </td>
                </tr>
              )}
            </Fragment>

          ))}
        </DataTable>
        </div>
      )}
    </div>
  );
}
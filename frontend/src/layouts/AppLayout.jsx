import { useState , useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Search, ShieldAlert, BarChart3, Radio, Menu, X , UploadCloud  } from "lucide-react";
import ScanlineOverlay from "../components/ScanlineOverlay";
import { checkHealth } from "../api/client";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Log Analyzer", icon: UploadCloud },
  { to: "/explorer", label: "Log Explorer", icon: Search },
  { to: "/alerts", label: "Alerts", icon: ShieldAlert },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [now, setNow] = useState(new Date());
  const [backendStatus, setBackendStatus] = useState("checking");

 useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const check = () => {
      checkHealth()
        .then((data) => setBackendStatus(data.database === "connected" ? "connected" : "degraded"))
        .catch(() => setBackendStatus("unreachable"));
    };
    check();
    const healthTimer = setInterval(check, 10000); // recheck every 10s
    return () => clearInterval(healthTimer);
  }, []);
  const statusConfig = {
    checking: { color: "text-slate/50", dot: "bg-slate/50", label: "checking..." },
    connected: { color: "text-amber", dot: "bg-amber", label: "connected" },
    degraded: { color: "text-amber", dot: "bg-amber", label: "degraded" },
    unreachable: { color: "text-rust", dot: "bg-rust", label: "unreachable" },
  };
  const current = statusConfig[backendStatus];

  return (
    <div className="flex h-screen bg-void text-slate">
      <ScanlineOverlay />

      {/* Mobile overlay backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-void/70 z-30 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-60 border-r border-panel bg-panel/40 flex flex-col transition-transform duration-200 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="px-5 py-6 border-b border-panel flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-bone font-display font-semibold text-lg">
              <Radio size={20} className="text-amber" />
              LA-IDS
            </div>
            <p className="text-xs text-slate/60 mt-1 font-mono">log analysis & intrusion detection</p>
          </div>
          <button className="md:hidden text-slate/50" onClick={() => setMobileOpen(false)} aria-label="Close menu">
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber ${
                  isActive
                    ? "bg-amber/10 text-amber border-l-2 border-amber"
                    : "text-slate/70 hover:bg-panel hover:text-bone"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-panel">
          <div className="flex items-center gap-2 text-xs text-slate/60">
            <span className="w-2 h-2 rounded-full bg-amber animate-pulse" />
            monitoring active
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-panel flex items-center justify-between px-4 md:px-6">
          <button
            className="md:hidden text-slate/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber rounded"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
          <div className="font-mono text-xs text-slate/50 hidden sm:block">
            {now.toLocaleString()}
          </div>
            <div className="flex items-center gap-2 text-xs font-mono text-slate/50">
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot} ${backendStatus === "connected" ? "animate-pulse" : ""}`} />
      backend: <span className={current.color}>{current.label}</span>
    </div>

        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
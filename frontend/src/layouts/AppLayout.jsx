import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Search, ShieldAlert, BarChart3, Radio } from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/explorer", label: "Log Explorer", icon: Search },
  { to: "/alerts", label: "Alerts", icon: ShieldAlert },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-void text-slate">
      {/* Sidebar */}
      <aside className="w-60 border-r border-panel bg-panel/40 flex flex-col">
        <div className="px-5 py-6 border-b border-panel">
          <div className="flex items-center gap-2 text-bone font-display font-semibold text-lg">
            <Radio size={20} className="text-amber" />
            LA-IDS
          </div>
          <p className="text-xs text-slate/60 mt-1 font-mono">log analysis & intrusion detection</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
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
        <header className="h-16 border-b border-panel flex items-center justify-between px-6">
          <div className="font-mono text-xs text-slate/50">
            {new Date().toLocaleString()}
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate/50">
            backend: <span className="text-amber">connected</span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
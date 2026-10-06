import { NavLink } from "react-router-dom";
import { LayoutDashboard, HeartPulse, BarChart3, TrendingUp, Wallet, MessageCircle, Settings, Download } from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/health-score", label: "Health Score", icon: HeartPulse },
  { to: "/kpi-analysis", label: "KPI Analysis", icon: BarChart3 },
  { to: "/trends", label: "Trends", icon: TrendingUp },
  { to: "/spending", label: "My Spending", icon: Wallet },
  { to: "/insight", label: "Insight", icon: MessageCircle },
  { to: "/details", label: "My Details", icon: Settings },
  { to: "/export", label: "Export", icon: Download },
];

export default function Topbar() {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#1e3a5f] flex items-center justify-center text-white font-bold text-sm">
            C
          </div>
          <span className="text-lg font-bold text-slate-800 tracking-tight">Credo</span>
        </div>

        <nav className="flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#eef2f7] text-[#1e3a5f]"
                    : "text-slate-500 hover:text-slate-800 hover:bg-slate-50"
                }`
              }
            >
              <Icon size={16} />
              <span className="hidden lg:inline">{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}

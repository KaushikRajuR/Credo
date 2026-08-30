import { NavLink } from "react-router-dom";
import { LayoutDashboard, HeartPulse, SlidersHorizontal, GitCompare, MessageCircle, Settings } from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/health-score", label: "Financial Health Score", icon: HeartPulse },
  { to: "/shift", label: "Shift", icon: SlidersHorizontal },
  { to: "/past-present", label: "Past vs Present", icon: GitCompare },
  { to: "/insight", label: "Insight", icon: MessageCircle },
  { to: "/details", label: "My Details", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-white border-r border-slate-200 flex flex-col fixed left-0 top-0">
      <div className="px-6 py-6 border-b border-slate-100">
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Credo</h1>
        <p className="text-xs text-slate-400 mt-1">MSME Financial Health</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-teal-50 text-teal-700"
                  : "text-slate-600 hover:bg-slate-50"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
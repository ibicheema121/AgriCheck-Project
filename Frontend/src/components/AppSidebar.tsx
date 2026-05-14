import { LayoutDashboard, Bot, History, Settings, Leaf, LogOut, ChevronLeft, ChevronRight, X } from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { motion } from "framer-motion";

const navItems = [
  { key: "dashboard" as const, path: "/dashboard", icon: LayoutDashboard },
  { key: "aiAdvisor" as const, path: "/ai-advisor", icon: Bot },
  { key: "soilHistory" as const, path: "/soil-history", icon: History },
  { key: "settings" as const, path: "/settings", icon: Settings },
];

interface AppSidebarProps {
  collapsed?: boolean;
  open?: boolean;
  onToggleCollapse?: () => void;
  onToggleOpen?: () => void;
}

export function AppSidebar({ collapsed = false, open = false, onToggleCollapse, onToggleOpen }: AppSidebarProps) {
  const { t } = useLanguage();
  const { logout } = useAuth();
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay backdrop */}
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onToggleOpen}
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
        />
      )}

      <aside className={`fixed md:static min-h-screen bg-sidebar flex flex-col border-e border-sidebar-border shrink-0 transition-all duration-300 ease-in-out z-50 ${
        open ? "w-64 translate-x-0" : "w-64 -translate-x-full md:translate-x-0"
      } ${
        collapsed ? "md:w-20" : "md:w-64"
      }`}>
        {/* Logo & Collapse Button */}
        <div className={`px-6 py-4 flex items-center gap-3 justify-between`}>
          <div className={`flex items-center gap-3 ${collapsed ? "hidden md:flex justify-center flex-1" : ""}`}>
            <div className="w-10 h-10 rounded-xl bg-sidebar-primary/20 flex items-center justify-center shrink-0">
              <Leaf className="w-6 h-6 text-sidebar-primary" />
            </div>
            {!collapsed && (
              <span className="text-xl font-bold text-sidebar-foreground tracking-tight whitespace-nowrap">
                {t("appName")}
              </span>
            )}
          </div>

          {/* Close button for mobile */}
          <button
            onClick={onToggleOpen}
            className="md:hidden flex items-center justify-center w-9 h-9 rounded-lg text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors shrink-0"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Collapse button for desktop */}
          <button
            onClick={onToggleCollapse}
            className="hidden md:flex items-center justify-center w-9 h-9 rounded-lg text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors shrink-0"
            aria-label="Toggle sidebar collapse"
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 mt-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <div key={item.key} className="relative group">
              <NavLink
                to={item.path}
                className="relative block"
                title={collapsed ? t(item.key) : undefined}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-sidebar-accent"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <div className={`relative flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive
                    ? "text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
                  } ${collapsed ? "justify-center" : ""}`}>
                  <item.icon className="w-5 h-5 shrink-0" />
                  {!collapsed && <span>{t(item.key)}</span>}
                </div>
              </NavLink>
              
              {/* Tooltip for collapsed state */}
              {collapsed && (
                <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-2 bg-sidebar-accent text-sidebar-accent-foreground text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                  {t(item.key)}
                </div>
              )}
            </div>
          );
        })}
      </nav>

        {/* Logout */}
        <div className={`p-3 border-t border-sidebar-border ${collapsed ? "flex justify-center" : ""}`}>
          <button
            onClick={logout}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors ${collapsed ? "justify-center" : "w-full"}`}
            title={collapsed ? t("logout") : undefined}
          >
            <LogOut className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{t("logout")}</span>}
          </button>
        </div>
      </aside>
    </>
  );
}

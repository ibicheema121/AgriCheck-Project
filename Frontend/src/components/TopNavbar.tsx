import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { Bell, User, Menu, X } from "lucide-react";

interface TopNavbarProps {
  onToggleSidebar?: () => void;
  sidebarOpen?: boolean;
}

export function TopNavbar({ onToggleSidebar, sidebarOpen = false }: TopNavbarProps) {
  const { language, setLanguage, t } = useLanguage();
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-border bg-card/80 backdrop-blur-sm flex items-center justify-between px-4 sm:px-6 shrink-0 gap-4">
      {/* Sidebar Toggle for Mobile */}
      <button
        onClick={onToggleSidebar}
        className="flex items-center justify-center w-9 h-9 rounded-lg bg-muted text-muted-foreground hover:text-foreground transition-colors md:hidden"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      <div className="flex-1 min-w-0">
        <h2 className="text-base sm:text-lg font-semibold text-foreground truncate">{t("sensorOverview")}</h2>
        <p className="text-xs text-muted-foreground hidden sm:block">{t("realTimeMonitoring")}</p>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        {/* Language Toggle */}
        <div className="flex items-center bg-muted rounded-lg p-0.5 text-xs sm:text-sm font-medium">
          <button
            onClick={() => setLanguage("en")}
            className={`px-2 sm:px-3 py-1.5 rounded-md transition-all text-xs sm:text-sm ${
              language === "en"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage("ur")}
            className={`px-2 sm:px-3 py-1.5 rounded-md transition-all font-urdu text-xs sm:text-sm ${
              language === "ur"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            اردو
          </button>
        </div>

        {/* Notifications */}
        <button className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors shrink-0">
          <Bell className="w-4 h-4" />
        </button>

        {/* User */}
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
            <User className="w-4 h-4 text-primary" />
          </div>
          <span className="text-sm font-medium text-foreground hidden md:block truncate">
            {user?.name}
          </span>
        </div>
      </div>
    </header>
  );
}

import { useState } from "react";
import { Outlet } from "react-router-dom";
import { AppSidebar } from "./AppSidebar";
import { TopNavbar } from "./TopNavbar";
import { VoiceAdvisorButton } from "./VoiceAdvisorButton";
import { ChatAssistant } from "./ChatAssistant";

export function DashboardLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebarCollapse = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const toggleSidebarOpen = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="min-h-screen flex w-full bg-background">
      <AppSidebar 
        collapsed={sidebarCollapsed} 
        open={sidebarOpen}
        onToggleCollapse={toggleSidebarCollapse}
        onToggleOpen={toggleSidebarOpen}
      />
      <div className="flex-1 flex flex-col min-h-screen">
        <TopNavbar onToggleSidebar={toggleSidebarOpen} sidebarOpen={sidebarOpen} />
        <main className="flex-1 overflow-auto relative">
          <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6">
            <Outlet />
          </div>
        </main>
      </div>
      <VoiceAdvisorButton />
      {/* <ChatAssistant /> */}
    </div>
  );
}

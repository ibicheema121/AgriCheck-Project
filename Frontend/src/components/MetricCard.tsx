import { motion } from "framer-motion";
import { useLanguage } from "@/contexts/LanguageContext";
import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  unit: string;
  status: "good" | "optimal" | "high" | "low" | "moderate";
  color: string;
  index: number;
}

const statusColors: Record<string, string> = {
  good: "bg-success/10 text-success",
  optimal: "bg-primary/10 text-primary",
  high: "bg-warning/10 text-warning",
  low: "bg-info/10 text-info",
  moderate: "bg-muted text-muted-foreground",
};

export function MetricCard({ icon: Icon, label, value, unit, status, color, index }: MetricCardProps) {
  const { t } = useLanguage();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      className="metric-card group bg-card/90 backdrop-blur-md"
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1.5">
          <span className="live-dot" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-success">
            {t("live")}
          </span>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-1">{label}</p>

      <div className="flex items-baseline gap-2">
        <motion.span
          key={value}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-3xl font-bold text-foreground tabular-nums"
        >
          {value}
        </motion.span>
        <span className="text-sm text-muted-foreground">{unit}</span>
      </div>

      <div className="mt-3">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status]}`}>
          {t(status)}
        </span>
      </div>
    </motion.div>
  );
}

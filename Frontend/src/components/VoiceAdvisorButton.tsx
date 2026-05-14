import { useNavigate } from "react-router-dom";
import { Mic } from "lucide-react";
import { motion } from "framer-motion";
import { useLanguage } from "@/contexts/LanguageContext";

export function VoiceAdvisorButton() {
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/ai-advisor");
  };

  return (
    <div className="fixed bottom-6 end-6 z-50 flex flex-col items-center gap-2">
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={handleClick}
        className="w-16 h-16 rounded-full flex items-center justify-center text-primary-foreground transition-all bg-primary ai-glow animate-glow-breathe hover:shadow-lg"
        title={t("aiTapToSpeak")}
      >
        <Mic className="w-6 h-6" />
      </motion.button>

      <span className="text-[10px] text-muted-foreground font-medium">
        {t("aiAdvisor")}
      </span>
    </div>
  );
}

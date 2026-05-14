import { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { MessageCircle, X, Send, Bot, User, Leaf, Loader2, AlertCircle } from "lucide-react";
import { chatService, type AdvisorChatRequest } from "@/services/chatService";
import { sensorService } from "@/services/sensorService";

// Simple UUID-like generation
const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/* ─── Types ─── */
interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  ts: Date;
}


/* ─── Component ─── */
export function ChatAssistant() {
  const location = useLocation();
  const isHome = location.pathname === "/";
  const isAIAdvisor = location.pathname === "/ai-advisor";

  const initialGreeting = isHome
    ? "👋 Hi! I'm AgriCheck's Public AI assistant. Ask anything about crops, soil, weather and farming tips."
    : "👋 Hi! I'm AgriCheck's AI Advisor. Ask me about your soil health, irrigation advice, fertilizer recommendations, and more!";

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "initial",
      role: "assistant",
      text: initialGreeting,
      ts: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasUnread, setHasUnread] = useState(true);
  const [sessionId] = useState(() => {
    // Try to get from session storage, otherwise generate new
    const stored = sessionStorage.getItem("agricheck_session_id");
    if (stored) return stored;
    const newId = generateId();
    sessionStorage.setItem("agricheck_session_id", newId);
    return newId;
  });
  const [landSize, setLandSize] = useState(1.0);
  const [includeSensorData, setIncludeSensorData] = useState(true);
  const [sensorDataAvailable, setSensorDataAvailable] = useState(true);
  const [showOptions, setShowOptions] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setHasUnread(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  useEffect(() => {
    if (isHome) return;

    // If no sensor data exists yet, keep advisor path usable by falling back.
    sensorService
      .getLatest()
      .then(() => {
        setSensorDataAvailable(true);
        setIncludeSensorData(true);
      })
      .catch(() => {
        setSensorDataAvailable(false);
        setIncludeSensorData(false);
      });
  }, [isHome]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string = input, retry = false) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
      ts: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      if (isHome) {
        const response = await chatService.publicChat(trimmed, "auto");

        const reply: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: response.response,
          ts: new Date(),
        };

        setMessages((prev) => [...prev, reply]);
        return;
      }

      const request: AdvisorChatRequest = {
        message: trimmed,
        session_id: sessionId,
        land_size_acres: landSize,
        include_sensor_data: includeSensorData,
      };

      const response = await chatService.advisorChat(request);

      const reply: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        text: response.response,
        ts: new Date(),
      };

      setMessages((prev) => [...prev, reply]);
    } catch (err) {
      const rawMessage = err instanceof Error ? err.message : "Unknown error";

      if (
        !isHome &&
        !retry &&
        includeSensorData &&
        rawMessage.toLowerCase().includes("nonetype")
      ) {
        // Backend likely failed due to missing sensor data; retry without sensors.
        setIncludeSensorData(false);
        setSensorDataAvailable(false);
        await sendMessage(trimmed, true);
        return;
      }

      const errorMsg =
        err instanceof Error
          ? err.message
          : "Failed to get AI response. Please ensure the backend is running.";
      setError(errorMsg);
      console.error("Chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (d: Date) =>
    d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const clearChat = () => {
    setMessages([
      {
        id: "initial",
        role: "assistant",
        text: "👋 Hi! I'm AgriCheck's AI Advisor. Ask me about your soil health, irrigation advice, fertilizer recommendations, and more!",
        ts: new Date(),
      },
    ]);
    setError(null);
  };

  return (
    <>
      {/* ── Chat Popup ── */}
      <div
        className={`fixed bottom-24 right-6 z-50 w-[340px] sm:w-[380px] transition-all duration-300 ${open
            ? "opacity-100 translate-y-0 pointer-events-auto"
            : "opacity-0 translate-y-6 pointer-events-none"
          }`}
        aria-hidden={!open}
      >
        <div
          className="rounded-2xl shadow-2xl border border-border bg-card flex flex-col overflow-hidden"
          style={{ height: "520px" }}
        >
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 bg-primary text-primary-foreground shrink-0">
            <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
              <Leaf className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-sm">
                {isHome ? "AgriCheck Public Chat" : "AgriCheck AI Advisor"}
              </div>
              <div className="flex items-center gap-1.5 text-xs text-primary-foreground/80">
                <span className="w-1.5 h-1.5 rounded-full bg-green-300 animate-pulse" />
                Online
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="w-8 h-8 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          {!isHome && !sensorDataAvailable && (
            <div className="px-4 py-2 text-xs text-yellow-700 bg-yellow-100 border border-yellow-200 rounded mb-2">
              Sensor data unavailable, using generic advisor output. You can upload a sensor reading and retry for improved recommendations.
            </div>
          )}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-background/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-end gap-2 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
              >
                {/* Avatar */}
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${msg.role === "assistant" ? "bg-primary/10" : "bg-muted"
                    }`}
                >
                  {msg.role === "assistant" ? (
                    <Bot className="w-4 h-4 text-primary" />
                  ) : (
                    <User className="w-4 h-4 text-muted-foreground" />
                  )}
                </div>

                {/* Bubble */}
                <div
                  className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed whitespace-pre-line ${msg.role === "assistant"
                      ? "bg-card border border-border text-foreground rounded-bl-sm"
                      : "bg-primary text-primary-foreground rounded-br-sm"
                    }`}
                >
                  {msg.text}
                  <div
                    className={`text-[10px] mt-1 ${msg.role === "assistant"
                        ? "text-muted-foreground"
                        : "text-primary-foreground/60"
                      }`}
                  >
                    {formatTime(msg.ts)}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex items-end gap-2">
                <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="flex gap-1 px-3 py-2 bg-card border border-border rounded-2xl rounded-bl-sm">
                  <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" />
                  <div
                    className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-destructive mt-0.5 shrink-0" />
                <p className="text-xs text-destructive">{error}</p>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {!isHome && (
            <>
              {/* Options Toggle */}
              <button
                onClick={() => setShowOptions(!showOptions)}
                className="text-xs text-muted-foreground hover:text-foreground px-4 py-2 transition-colors border-t border-border"
              >
                {showOptions ? "Hide Options ▲" : "Show Options ▼"}
              </button>

              {/* Advanced Options */}
              {showOptions && (
                <div className="px-4 py-3 bg-muted/30 border-t border-border space-y-3">
                  <div>
                    <label className="text-xs font-semibold text-muted-foreground">
                      Land Size (acres)
                    </label>
                    <input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={landSize}
                      onChange={(e) =>
                        setLandSize(parseFloat(e.target.value) || 1)
                      }
                      className="w-full text-xs mt-1 px-2 py-1 rounded border border-border bg-background"
                    />
                  </div>
                  <label className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeSensorData}
                      onChange={(e) => setIncludeSensorData(e.target.checked)}
                      className="w-4 h-4 rounded"
                    />
                    <span>Include latest sensor data</span>
                  </label>
                </div>
              )}
            </>
          )}

          {/* Input Area */}
          <div className="px-3 py-3 bg-background border-t border-border shrink-0 space-y-2">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                placeholder="Ask about your crops..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={loading}
                className="flex-1 px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition disabled:opacity-50"
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="w-9 h-9 rounded-lg bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            {messages.length > 1 && (
              <button
                onClick={clearChat}
                className="w-full text-xs px-3 py-1.5 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                Clear Chat
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Floating Chat Button ── */}
      <button
        onClick={() => setOpen((v) => !v)}
        className={`fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full shadow-xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 ${open
            ? "bg-destructive text-destructive-foreground"
            : "bg-primary text-primary-foreground"
          }`}
        aria-label="Toggle chat assistant"
      >
        {open ? (
          <X className="w-6 h-6" />
        ) : (
          <MessageCircle className="w-6 h-6" />
        )}

        {/* Unread badge */}
        {hasUnread && !open && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center animate-bounce">
            1
          </span>
        )}
      </button>
    </>
  );
}

import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radio,
  Loader2,
  Mic,
  MicOff,
  AlertCircle,
  Volume2,
  Leaf,
  Send,
  Settings,
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { chatService, type AdvisorChatRequest } from "@/services/chatService";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Message {
  type:
    | "status"
    | "transcription"
    | "ai_response"
    | "mute_mic"
    | "unmute_mic"
    | "audio_playback"
    | "error"
    | "info";
  text: string;
  timestamp: Date;
  language?: string;
}

interface TextMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  ts: Date;
}

// ---------------------------------------------------------------------------
// Helpers (module-level, no closure issues)
// ---------------------------------------------------------------------------

/** Derive ws:// or wss:// URL from VITE_API_BASE_URL. */
function buildWsUrl(): string {
  const apiBase =
    import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:8000";

  return apiBase
    .replace(/^https:\/\//, "wss://")
    .replace(/^http:\/\//, "ws://")
    .replace(/\/$/, "") // strip trailing slash if any
    .concat("/voice/ws/voice-advisor");
}

/** Safely decode a base64 string into a Uint8Array. Returns null on failure. */
function base64ToBytes(base64: string): Uint8Array | null {
  try {
    if (!base64) return null;
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  } catch {
    return null;
  }
}

/** Detect audio MIME type from the first 4 bytes of a buffer. */
function detectMimeType(bytes: Uint8Array): string {
  if (bytes.length < 4) return "audio/wav";

  const [b0, b1, b2, b3] = bytes;

  // MP3
  if (b0 === 0xff && (b1 & 0xe0) === 0xe0) return "audio/mpeg";
  // WAV (RIFF)
  if (b0 === 0x52 && b1 === 0x49 && b2 === 0x46 && b3 === 0x46)
    return "audio/wav";
  // OGG
  if (b0 === 0x4f && b1 === 0x67 && b2 === 0x67 && b3 === 0x53)
    return "audio/ogg";

  return "audio/wav";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AIAdvisor() {
  const { t } = useLanguage();
  const { user } = useAuth();

  // ── Voice messages ────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([
    { type: "info", text: t("voiceAdvisorReady"), timestamp: new Date() },
  ]);

  // ── WebSocket / recording state ───────────────────────────────────────────
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // ── Text chat state ───────────────────────────────────────────────────────
  const [textMessages, setTextMessages] = useState<TextMessage[]>([
    { id: "welcome", role: "assistant", text: t("welcomeChat"), ts: new Date() },
  ]);
  const [textQuestion, setTextQuestion] = useState("");
  const [textLoading, setTextLoading] = useState(false);
  const [textError, setTextError] = useState<string | null>(null);

  // ── Shared config ─────────────────────────────────────────────────────────
  const [landSize, setLandSize] = useState(1.0);
  const [showSettings, setShowSettings] = useState(false);

  // ── Refs ──────────────────────────────────────────────────────────────────
  // IMPORTANT: isRecordingRef and isMicMutedRef are the source-of-truth for
  // the onaudioprocess callback to avoid stale closures. They must always be
  // kept in sync with the corresponding state setters below.
  const isRecordingRef = useRef(false);
  const isMicMutedRef = useRef(false);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const audioChunksRef = useRef<Uint8Array[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // ── Auto-scroll ───────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Cleanup on unmount ────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      // Stop microphone tracks
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
      scriptProcessorRef.current?.disconnect();
      audioContextRef.current?.close();
      // Close WebSocket without triggering state updates (component is gone)
      if (wsRef.current) {
        wsRef.current.onclose = null; // prevent setState after unmount
        wsRef.current.close();
      }
    };
  }, []);

  // ── Helpers ───────────────────────────────────────────────────────────────

  const addMessage = useCallback(
    (type: Message["type"], text: string, language?: string) => {
      setMessages((prev) => [
        ...prev,
        { type, text, timestamp: new Date(), language },
      ]);
    },
    []
  );

  /** Sync both state and ref together. */
  const setRecording = (val: boolean) => {
    isRecordingRef.current = val;
    setIsRecording(val);
  };

  const setMicMuted = (val: boolean) => {
    isMicMutedRef.current = val;
    setIsMicMuted(val);
  };

  // ── Audio playback ────────────────────────────────────────────────────────

  const notifyPlaybackEnded = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "audio_playback_ended" }));
    }
  }, []);

  const playAudioChunks = useCallback(() => {
    const chunks = audioChunksRef.current;

    if (chunks.length === 0) {
      addMessage("info", "⚠️ No audio to play");
      notifyPlaybackEnded();
      return;
    }

    // Combine all chunks into a single buffer
    const totalLength = chunks.reduce((sum, c) => sum + c.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
      combined.set(chunk, offset);
      offset += chunk.length;
    }
    audioChunksRef.current = []; // clear immediately

    const mimeType = detectMimeType(combined);
    addMessage("info", `🎵 Audio format: ${mimeType}`);

    const blob = new Blob([combined], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const player = audioPlayerRef.current;

    if (!player) {
      notifyPlaybackEnded();
      URL.revokeObjectURL(url);
      return;
    }

    player.src = url;

    player.onerror = () => {
      addMessage("error", "❌ Failed to play audio. Try a different browser.");
      notifyPlaybackEnded();
      URL.revokeObjectURL(url);
    };

    player.onended = () => {
      notifyPlaybackEnded();
      URL.revokeObjectURL(url);
    };

    player.play().catch((err: Error) => {
      addMessage("error", `❌ Playback failed: ${err.message}`);
      notifyPlaybackEnded();
      URL.revokeObjectURL(url);
    });
  }, [addMessage, notifyPlaybackEnded]);

  // ── WebSocket ─────────────────────────────────────────────────────────────

  const connectWebSocket = useCallback(async () => {
    // Prevent double-connect
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setIsLoading(true);
    setWsError(null);

    const wsUrl = buildWsUrl();
    addMessage("info", t("connectingToVoiceAdvisor"));

    let ws: WebSocket;
    try {
      ws = new WebSocket(wsUrl);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Invalid WebSocket URL";
      setWsError(msg);
      addMessage("error", `❌ ${msg}`);
      setIsLoading(false);
      return;
    }

    ws.binaryType = "arraybuffer"; // explicit, avoids browser quirks

    ws.onopen = () => {
      setIsConnected(true);
      setIsLoading(false);
      addMessage("status", t("connectedToVoiceAdvisor"));
      // Send initial config
      ws.send(JSON.stringify({ type: "config", land_size_acres: landSize }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string);

        switch (data.type) {
          case "status":
            addMessage("status", `📢 ${data.message}`);
            break;

          case "transcription":
            addMessage(
              "transcription",
              `${t("youSaid")}: ${data.text}`,
              data.language
            );
            break;

          case "ai_response":
            addMessage("ai_response", `🤖 ${data.text}`);
            break;

          case "audio_chunk": {
            const bytes = base64ToBytes(data.data);
            if (bytes) {
              audioChunksRef.current.push(bytes);
              addMessage(
                "info",
                `📥 Received audio chunk (${audioChunksRef.current.length} chunks)`
              );
            } else {
              addMessage("info", "⚠️ Skipped malformed audio chunk");
            }
            break;
          }

          case "mute_mic":
            setMicMuted(true);
            addMessage("mute_mic", t("micMutedAiResponding"));
            break;

          case "unmute_mic":
            setMicMuted(false);
            addMessage("unmute_mic", t("micUnmutedSpeakNow"));
            break;

          case "completed":
            addMessage("audio_playback", t("audioReceivedPlaying"));
            playAudioChunks();
            break;

          case "error":
            addMessage("error", `❌ ${data.message}`);
            break;

          case "keep_alive":
          case "pong":
            break;

          default:
            console.warn("Unknown WS message type:", data.type);
        }
      } catch (e) {
        console.error("Error parsing WS message:", e);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setRecording(false);
      setMicMuted(false);
      addMessage(
        "status",
        event.wasClean
          ? t("disconnected")
          : `${t("disconnected")} (code ${event.code})`
      );
    };

    ws.onerror = () => {
      // onerror always fires before onclose; let onclose handle state cleanup.
      const msg =
        "WebSocket connection failed. Check that the backend is reachable.";
      setWsError(msg);
      setIsLoading(false);
      addMessage("error", `❌ ${msg}`);
      // NOTE: do NOT call setState for isConnected here; onclose will fire next.
    };

    wsRef.current = ws;
  }, [addMessage, landSize, playAudioChunks, t]);

  const disconnectWebSocket = useCallback(() => {
    stopRecording();
    if (wsRef.current) {
      wsRef.current.close(1000, "User disconnected");
      wsRef.current = null;
    }
    setIsConnected(false);
    setWsError(null);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateConfig = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ type: "config", land_size_acres: landSize })
      );
      addMessage("info", `⚙️ Updated land size: ${landSize} acres`);
    }
  }, [addMessage, landSize]);

  // ── Recording ─────────────────────────────────────────────────────────────

  const startRecording = useCallback(async () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      const msg = "Connect to Voice Advisor before recording.";
      setWsError(msg);
      addMessage("error", `❌ ${msg}`);
      return;
    }

    setIsLoading(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      const AudioCtx =
        window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioContext = new AudioCtx({ sampleRate: 16000 });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      // IMPORTANT: capture the ws reference at connection time.
      // Do NOT access wsRef.current inside here — that would be a stale closure
      // for the ws object itself. Instead we read through wsRef at call time.
      scriptProcessor.onaudioprocess = (event) => {
        // Use refs (not state) to avoid stale closures
        if (
          !isRecordingRef.current ||
          isMicMutedRef.current ||
          !wsRef.current ||
          wsRef.current.readyState !== WebSocket.OPEN
        ) {
          return;
        }

        const inputData = event.inputBuffer.getChannelData(0);
        const pcm16 = new Int16Array(inputData.length);

        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        wsRef.current.send(pcm16.buffer);
      };

      source.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      setRecording(true);
      setMicMuted(false);
      setIsLoading(false);
      addMessage("status", "📊 Audio: 16000 Hz · Mono · 16-bit PCM");
      addMessage("status", t("recordingSpeakNow"));
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Microphone access denied";
      setWsError(msg);
      addMessage("error", `❌ Microphone error: ${msg}`);
      setIsLoading(false);
    }
  }, [addMessage, t]);

  const stopRecording = useCallback(() => {
    setRecording(false);
    setMicMuted(false);

    scriptProcessorRef.current?.disconnect();
    scriptProcessorRef.current = null;

    audioContextRef.current?.close();
    audioContextRef.current = null;

    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    mediaStreamRef.current = null;

    addMessage("status", t("disconnected"));
  }, [addMessage, t]);

  // ── Text chat ─────────────────────────────────────────────────────────────
  // Completely independent from the WebSocket — failures here don't affect voice.

  const sendTextQuery = useCallback(async () => {
    const trimmed = textQuestion.trim();
    if (!trimmed) return;

    setTextError(null);
    setTextLoading(true);
    setTextQuestion("");

    setTextMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, role: "user", text: trimmed, ts: new Date() },
    ]);

    try {
      const request: AdvisorChatRequest = {
        message: trimmed,
        land_size_acres: landSize,
        include_sensor_data: true,
      };

      const response = await chatService.advisorChat(request);

      setTextMessages((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: response.response,
          ts: new Date(),
        },
      ]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to connect to AI advisor.";
      setTextError(message);
      console.error("Advisor text query error:", err);
    } finally {
      setTextLoading(false);
    }
  }, [textQuestion, landSize]);

  // ── UI helpers ────────────────────────────────────────────────────────────

  const getMessageColor = (type: Message["type"]) => {
    switch (type) {
      case "status":
        return "text-blue-600 dark:text-blue-400";
      case "transcription":
        return "text-green-600 dark:text-green-400";
      case "ai_response":
        return "text-purple-600 dark:text-purple-400";
      case "mute_mic":
      case "unmute_mic":
        return "text-orange-600 dark:text-orange-400";
      case "error":
        return "text-red-600 dark:text-red-400";
      default:
        return "text-gray-600 dark:text-gray-400";
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start sm:items-center gap-2 sm:gap-3 mb-4 sm:mb-6 px-0.5">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
            <Leaf className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-bold text-foreground">
              {t("aiAdvisorHeading")}
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground line-clamp-2">
              {t("aiAdvisorSubheading")}
            </p>
          </div>
        </div>
      </motion.div>

      {/* WebSocket Error Alert */}
      <AnimatePresence>
        {wsError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{wsError}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className={`rounded-lg px-4 py-3 font-semibold flex items-center gap-3 ${
          isConnected
            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
            : isLoading
            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
            : isMicMuted
            ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400"
            : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
        }`}
      >
        <Radio className="w-5 h-5" />
        <span>
          {isConnected && !isRecording && `🟢 ${t("connected")}`}
          {isConnected && isRecording && !isMicMuted && `🎤 ${t("recordingSpeakNow")}`}
          {isMicMuted && `🔇 ${t("micMutedAiResponding")}`}
          {isLoading && `⏳ ${t("connecting")}`}
          {!isConnected && !isLoading && `🔌 ${t("disconnected")}`}
        </span>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 sm:gap-6 px-0.5">
        {/* Controls & Settings */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="md:col-span-1 space-y-2 sm:space-y-3"
        >
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">{t("controls")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                onClick={isConnected ? disconnectWebSocket : connectWebSocket}
                disabled={isLoading}
                className="w-full"
                variant={isConnected ? "destructive" : "default"}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                {isConnected ? t("disconnect") : t("connect")}
              </Button>

              <Button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={!isConnected || isLoading}
                className="w-full"
                variant={isRecording ? "secondary" : "outline"}
              >
                {isRecording ? (
                  <>
                    <MicOff className="w-4 h-4 mr-2" />
                    {t("stopRecording")}
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4 mr-2" />
                    {t("startRecording")}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Settings */}
          <Card>
            <CardHeader className="pb-3">
              <button
                onClick={() => setShowSettings((s) => !s)}
                className="flex items-center justify-between w-full hover:opacity-75 transition"
              >
                <CardTitle className="text-sm">{t("settings")}</CardTitle>
                <Settings className="w-4 h-4" />
              </button>
            </CardHeader>
            <AnimatePresence>
              {showSettings && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ overflow: "hidden" }}
                >
                  <CardContent className="space-y-3">
                    <div>
                      <label className="text-xs font-semibold text-muted-foreground block mb-2">
                        {t("landSizeAcres")}
                      </label>
                      <Input
                        type="number"
                        min="0.1"
                        step="0.1"
                        value={landSize}
                        onChange={(e) =>
                          setLandSize(parseFloat(e.target.value) || 1)
                        }
                        className="text-xs"
                      />
                    </div>
                    <Button
                      onClick={updateConfig}
                      disabled={!isConnected}
                      size="sm"
                      className="w-full"
                    >
                      {t("updateConfig")}
                    </Button>
                  </CardContent>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          {/* Audio Player */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Volume2 className="w-4 h-4" />
                {t("audioPlayback")}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <audio
                ref={audioPlayerRef}
                controls
                crossOrigin="anonymous"
                className="w-full h-10"
                controlsList="nodownload"
              >
                Your browser does not support the audio element.
              </audio>
              <p className="text-xs text-muted-foreground">
                {t("audioInstructions")}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Voice Messages */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t("messages")}</CardTitle>
              <CardDescription>
                {messages.length}{" "}
                {messages.length !== 1 ? t("messagesPlural") : t("message")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                <AnimatePresence>
                  {messages.map((msg, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className={`text-sm p-2 rounded font-mono ${getMessageColor(
                        msg.type
                      )}`}
                    >
                      <div className="flex justify-between items-start gap-2">
                        <div className="flex-1">{msg.text}</div>
                        <span className="text-xs opacity-60 whitespace-nowrap">
                          {msg.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      {msg.language && (
                        <div className="text-xs opacity-60 mt-1">
                          {t("languageLabel")}: {msg.language}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Text Chat — completely independent from WebSocket */}
      <Card className="w-full max-w-3xl mx-auto">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">{t("aiChatAssistant")}</CardTitle>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Chat Messages */}
          <div className="max-h-64 overflow-y-auto p-3 space-y-2 border border-border rounded-lg bg-muted/20 flex flex-col">
            {textMessages.map((msg) => (
              <div
                key={msg.id}
                className={`rounded-xl px-3 py-2 text-sm max-w-[80%] ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground self-end text-right"
                    : "bg-secondary text-secondary-foreground self-start text-left"
                }`}
              >
                <div>{msg.text}</div>
                <div className="text-[10px] opacity-70 mt-1">
                  {msg.ts.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Text Error (isolated — does not affect voice panel) */}
          {textError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{textError}</AlertDescription>
            </Alert>
          )}

          {/* Input */}
          <div className="flex gap-2">
            <Input
              placeholder={t("typeQuestionPlaceholder")}
              value={textQuestion}
              onChange={(e) => setTextQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendTextQuery();
                }
              }}
              disabled={textLoading}
            />
            <Button
              onClick={sendTextQuery}
              disabled={textLoading || !textQuestion.trim()}
              size="icon"
            >
              {textLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

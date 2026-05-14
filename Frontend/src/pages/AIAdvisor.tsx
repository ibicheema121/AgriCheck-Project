import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radio,
  Loader2,
  Mic,
  MicOff,
  AlertCircle,
  Volume2,
  Zap,
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

export default function AIAdvisor() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      type: "info",
      text: t("voiceAdvisorReady"),
      timestamp: new Date(),
    },
  ]);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [textMessages, setTextMessages] = useState<TextMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: t("welcomeChat"),
      ts: new Date(),
    },
  ]);
  const [textQuestion, setTextQuestion] = useState("");
  const [textLoading, setTextLoading] = useState(false);
  const [textError, setTextError] = useState<string | null>(null);

  const isRecordingRef = useRef(false);
  const isMicMutedRef = useRef(false);
  const [landSize, setLandSize] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const audioChunksRef = useRef<Uint8Array[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Connect to WebSocket
  // const connectWebSocket = async () => {
  //   try {
  //     setIsLoading(true);
  //     setError(null);

  //     const host = window.location.hostname || "localhost";
  //     const backendPort = "8000";
  //     const wsUrl = `ws://${host}:${backendPort}/voice/ws/voice-advisor`;

  //     addMessage("info", t("connectingToVoiceAdvisor"));

  //     const ws = new WebSocket(wsUrl);

  //     ws.onopen = () => {
  //       setIsConnected(true);
  //       setIsLoading(false);
  //       addMessage("status", t("connectedToVoiceAdvisor"));

  //       // Send initial config
  //       if (landSize) {
  //         ws.send(JSON.stringify({ type: "config", land_size_acres: landSize }));
  //       }
  //     };

  //     ws.onmessage = (event) => {
  //       try {
  //         const data = JSON.parse(event.data);

  //         switch (data.type) {
  //           case "status":
  //             addMessage("status", `📢 ${data.message}`);
  //             break;

  //           case "transcription":
  //             addMessage("transcription", `${t("youSaid")}: ${data.text}`, data.language);
  //             break;

  //           case "ai_response":
  //             addMessage("ai_response", `🤖 ${data.text}`);
  //             break;

  //           case "audio_chunk":
  //             audioChunksRef.current.push(base64ToBytes(data.data));
  //             addMessage("info", `📥 Received audio chunk (${audioChunksRef.current.length} chunks)`);
  //             break;

  //           case "mute_mic":
  //             setIsMicMuted(true);
  //             isMicMutedRef.current = true;
  //             addMessage("mute_mic", t("micMutedAiResponding"));
  //             break;

  //           case "unmute_mic":
  //             setIsMicMuted(false);
  //             isMicMutedRef.current = false;
  //             addMessage("unmute_mic", t("micUnmutedSpeakNow"));
  //             break;

  //           case "completed":
  //             addMessage("audio_playback", t("audioReceivedPlaying"));
  //             playAudioChunks();
  //             break;

  //           case "error":
  //             addMessage("error", `❌ ${data.message}`);
  //             break;

  //           case "keep_alive":
  //           case "pong":
  //             break;

  //           default:
  //             console.log("Unknown message type:", data.type);
  //         }
  //       } catch (e) {
  //         console.error("Error parsing message:", e);
  //       }
  //     };

  //     ws.onclose = () => {
  //       setIsConnected(false);
  //       setIsRecording(false);
  //       isRecordingRef.current = false;
  //       setIsMicMuted(false);
  //       isMicMutedRef.current = false;
  //       addMessage("status", t("disconnected"));
  //     };

  //     ws.onerror = () => {
  //       setError("Failed to connect to Voice Advisor. Ensure backend is running.");
  //       setIsConnected(false);
  //       setIsLoading(false);
  //       addMessage("error", t("websocketFailed"));
  //     };

  //     wsRef.current = ws;
  //   } catch (err) {
  //     const msg = err instanceof Error ? err.message : "Connection failed";
  //     setError(msg);
  //     addMessage("error", `❌ ${msg}`);
  //     setIsLoading(false);
  //   }
  // };

  const connectWebSocket = async () => {
  try {
    setIsLoading(true);
    setError(null);

    // ✅ Derive wss:// or ws:// from your existing VITE_API_BASE_URL env variable
    const apiBase =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

    const wsUrl = apiBase
      .replace(/^https:\/\//, "wss://")   // https://agricheck-production.up.railway.app → wss://...
      .replace(/^http:\/\//, "ws://")     // http://127.0.0.1:8000 → ws://...
      .concat("/voice/ws/voice-advisor"); // keep your existing backend path

    addMessage("info", t("connectingToVoiceAdvisor"));

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      setIsLoading(false);
      addMessage("status", t("connectedToVoiceAdvisor"));

      // Send initial config
      if (landSize) {
        ws.send(JSON.stringify({ type: "config", land_size_acres: landSize }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case "status":
            addMessage("status", `📢 ${data.message}`);
            break;
          case "transcription":
            addMessage("transcription", `${t("youSaid")}: ${data.text}`, data.language);
            break;
          case "ai_response":
            addMessage("ai_response", `🤖 ${data.text}`);
            break;
          case "audio_chunk":
            audioChunksRef.current.push(base64ToBytes(data.data));
            addMessage("info", `📥 Received audio chunk (${audioChunksRef.current.length} chunks)`);
            break;
          case "mute_mic":
            setIsMicMuted(true);
            isMicMutedRef.current = true;
            addMessage("mute_mic", t("micMutedAiResponding"));
            break;
          case "unmute_mic":
            setIsMicMuted(false);
            isMicMutedRef.current = false;
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
            console.log("Unknown message type:", data.type);
        }
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      setIsRecording(false);
      isRecordingRef.current = false;
      setIsMicMuted(false);
      isMicMutedRef.current = false;
      addMessage("status", t("disconnected"));
    };

    ws.onerror = () => {
      setError("Failed to connect to Voice Advisor. Ensure backend is running.");
      setIsConnected(false);
      setIsLoading(false);
      addMessage("error", t("websocketFailed"));
    };

    wsRef.current = ws;
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Connection failed";
    setError(msg);
    addMessage("error", `❌ ${msg}`);
    setIsLoading(false);
  }
};

  // Disconnect from WebSocket
  const disconnectWebSocket = () => {
    stopRecording();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setError(null);
  };

  // POST /chat/ text-based advisor (dashboard AI Advisor)
  const sendTextQuery = async () => {
    const trimmed = textQuestion.trim();
    if (!trimmed) return;

    setTextError(null);
    setTextLoading(true);

    const userText = trimmed;
    setTextQuestion("");
    setTextMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, role: "user", text: userText, ts: new Date() },
    ]);

    try {
      const request: AdvisorChatRequest = {
        message: userText,
        land_size_acres: landSize,
        include_sensor_data: true,
      };

      const response = await chatService.advisorChat(request);
      setTextMessages((prev) => [
        ...prev,
        { id: `assistant-${Date.now()}`, role: "assistant", text: response.response, ts: new Date() },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to connect to AI advisor.";
      setTextError(message);
      console.error("Advisor text query error:", err);
    } finally {
      setTextLoading(false);
    }
  };

  // Start recording audio
  const startRecording = async () => {
    try {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        const msg = 'Connect to Voice Advisor before recording.';
        setError(msg);
        addMessage('error', `❌ ${msg}`);
        return;
      }

      setIsLoading(true);

      const constraints = {
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      mediaStreamRef.current = stream;

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      scriptProcessor.onaudioprocess = (event) => {
        if (!isRecordingRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
        if (isMicMutedRef.current) return;

        const inputData = event.inputBuffer.getChannelData(0);
        const pcm16 = new Int16Array(inputData.length);

        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        wsRef.current?.send(pcm16.buffer);
      };

      source.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      setIsRecording(true);
      isRecordingRef.current = true;
      setIsMicMuted(false);
      isMicMutedRef.current = false;
      setIsLoading(false);
      addMessage("status", "📊 Audio: 16000Hz, Mono, 16-bit");
      addMessage("status", t("recordingSpeakNow"));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Microphone access denied";
      setError(msg);
      addMessage("error", `❌ Microphone error: ${msg}`);
      setIsLoading(false);
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    setIsRecording(false);
    isRecordingRef.current = false;
    setIsMicMuted(false);
    isMicMutedRef.current = false;

    if (scriptProcessorRef.current) {
      scriptProcessorRef.current.disconnect();
      scriptProcessorRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    addMessage("status", t("disconnected"));
  };

  // Update configuration
  const updateConfig = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "config", land_size_acres: landSize }));
      addMessage("info", `⚙️ Updated land size: ${landSize} acres`);
    }
  };

  // Helper functions
  const addMessage = (type: Message["type"], text: string, language?: string) => {
    setMessages((prev) => [
      ...prev,
      { type, text, timestamp: new Date(), language },
    ]);
  };

  const base64ToBytes = (base64: string): Uint8Array => {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  };

  const playAudioChunks = () => {
    if (audioChunksRef.current.length === 0) {
      addMessage("info", "⚠️ No audio to play");
      notifyPlaybackEnded();
      return;
    }

    const totalLength = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.length, 0);
    const combined = new Uint8Array(totalLength);

    let offset = 0;
    audioChunksRef.current.forEach((chunk) => {
      combined.set(chunk, offset);
      offset += chunk.length;
    });

    // Try multiple audio formats for better compatibility
    let audioBlob: Blob;

    // Check first few bytes for format detection
    const header = new Uint8Array(combined.slice(0, 4));
    if (
      header[0] === 0xFF &&
      (header[1] & 0xE0) === 0xE0
    ) {
      // MP3 format detected
      audioBlob = new Blob([combined], { type: "audio/mpeg" });
      addMessage("info", "🎵 Audio format: MP3");
    } else if (
      header[0] === 0x52 &&
      header[1] === 0x49 &&
      header[2] === 0x46 &&
      header[3] === 0x46
    ) {
      // WAV format detected (RIFF header)
      audioBlob = new Blob([combined], { type: "audio/wav" });
      addMessage("info", "🎵 Audio format: WAV");
    } else if (
      header[0] === 0x4F &&
      header[1] === 0x67 &&
      header[2] === 0x67 &&
      header[3] === 0x53
    ) {
      // OGG format detected
      audioBlob = new Blob([combined], { type: "audio/ogg" });
      addMessage("info", "🎵 Audio format: OGG");
    } else {
      // Default to WAV, but try audio/webm as fallback
      audioBlob = new Blob([combined], { type: "audio/wav;codec=opus" });
      addMessage("info", "🎵 Audio format: Default (WAV/WebM)");
    }

    const url = window.URL.createObjectURL(audioBlob);

    if (audioPlayerRef.current) {
      audioPlayerRef.current.src = url;

      // Add error handling
      audioPlayerRef.current.onerror = (e) => {
        console.error("Audio playback error:", e);
        addMessage("error", "❌ Failed to play audio. Try using a different browser.");
        notifyPlaybackEnded();
      };

      // Auto-play the audio
      audioPlayerRef.current
        .play()
        .catch((err) => {
          console.error("Audio play error:", err);
          addMessage("error", `❌ Playback failed: ${err.message}`);
        });

      audioPlayerRef.current.onended = () => {
        notifyPlaybackEnded();
        window.URL.revokeObjectURL(url);
      };
    }

    audioChunksRef.current = [];
  };

  const notifyPlaybackEnded = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "audio_playback_ended" }));
    }
  };

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

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start sm:items-center gap-2 sm:gap-3 mb-4 sm:mb-6 px-0.5">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
            <Leaf className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-bold text-foreground">{t("aiAdvisorHeading")}</h1>
            <p className="text-xs sm:text-sm text-muted-foreground line-clamp-2">
              {t("aiAdvisorSubheading")}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Error Alert */}
      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className={`rounded-lg px-4 py-3 font-semibold flex items-center gap-3 ${isConnected
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
                onClick={() => setShowSettings(!showSettings)}
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
                        onChange={(e) => setLandSize(parseFloat(e.target.value) || 1)}
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

          {/* Text chat to /chat/ endpoint (AI Advisor) */}

        </motion.div>

        {/* Messages */}
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
                {messages.length} {messages.length !== 1 ? t("messagesPlural") : t("message")}
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
                      className={`text-sm p-2 rounded font-mono ${getMessageColor(msg.type)}`}
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
                        <div className="text-xs opacity-60 mt-1">{t("languageLabel")}: {msg.language}</div>
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

    {/* Error Message */}
    {textError && (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{textError}</AlertDescription>
      </Alert>
    )}

    {/* Input Section */}
    <div className="flex gap-2">
      <Input
        placeholder={t("typeQuestionPlaceholder")}
        value={textQuestion}
        onChange={(e) => setTextQuestion(e.target.value)}
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

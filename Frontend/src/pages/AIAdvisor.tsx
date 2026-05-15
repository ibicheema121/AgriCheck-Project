import { useEffect, useState, useRef } from "react";
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

interface Message {
  type: "status" | "transcription" | "ai_response" | "mute_mic" | "unmute_mic" | "audio_playback" | "error" | "info";
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

  const [messages, setMessages] = useState<Message[]>([{ type: "info", text: t("voiceAdvisorReady"), timestamp: new Date() }]);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [textMessages, setTextMessages] = useState<TextMessage[]>([{ id: "welcome", role: "assistant", text: t("welcomeChat"), ts: new Date() }]);
  const [textQuestion, setTextQuestion] = useState("");
  const [textLoading, setTextLoading] = useState(false);
  const [textError, setTextError] = useState<string | null>(null);
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
  const isRecordingRef = useRef(false);
  const isMicMutedRef = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  // Helper: Base64 converter (Bohat zaroori hai!)
  const base64ToBytes = (base64: string): Uint8Array => {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  };

  const connectWebSocket = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const cleanBase = apiBase.endsWith('/') ? apiBase.slice(0, -1) : apiBase;
      const wsUrl = cleanBase.replace(/^https:\/\//, "wss://").replace(/^http:\/\//, "ws://").concat("/voice/ws/voice-advisor");

      addMessage("info", t("connectingToVoiceAdvisor"));
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        setIsLoading(false);
        addMessage("status", t("connectedToVoiceAdvisor"));
        if (landSize) ws.send(JSON.stringify({ type: "config", land_size_acres: landSize }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case "status": addMessage("status", `📢 ${data.message}`); break;
            case "transcription": addMessage("transcription", `${t("youSaid")}: ${data.text}`, data.language); break;
            case "ai_response": addMessage("ai_response", `🤖 ${data.text}`); break;
            case "audio_chunk": audioChunksRef.current.push(base64ToBytes(data.data)); break;
            case "mute_mic": setIsMicMuted(true); isMicMutedRef.current = true; addMessage("mute_mic", t("micMutedAiResponding")); break;
            case "unmute_mic": setIsMicMuted(false); isMicMutedRef.current = false; addMessage("unmute_mic", t("micUnmutedSpeakNow")); break;
            case "completed": addMessage("audio_playback", t("audioReceivedPlaying")); playAudioChunks(); break;
            case "error": addMessage("error", `❌ ${data.message}`); break;
          }
        } catch (e) { console.error("Error:", e); }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsRecording(false);
        isRecordingRef.current = false;
        addMessage("status", t("disconnected"));
      };

      ws.onerror = () => {
        setError("WebSocket failed.");
        setIsConnected(false);
        setIsLoading(false);
      };
      wsRef.current = ws;
    } catch (err) {
      setIsLoading(false);
      setError("Failed to connect.");
    }
  };

  const disconnectWebSocket = () => {
    stopRecording();
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    setIsConnected(false);
  };

  const playAudioChunks = () => {
    if (audioChunksRef.current.length === 0) return;
    const totalLength = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;
    audioChunksRef.current.forEach((chunk) => { combined.set(chunk, offset); offset += chunk.length; });
    const audioBlob = new Blob([combined], { type: "audio/mpeg" });
    const url = window.URL.createObjectURL(audioBlob);
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.src = url;
      audioPlayerRef.current.load();
      audioPlayerRef.current.play().catch(e => console.error(e));
      audioPlayerRef.current.onended = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify({ type: "audio_playback_ended" }));
        window.URL.revokeObjectURL(url);
      };
    }
    audioChunksRef.current = [];
  };

  const startRecording = async () => {
    try {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
      setIsLoading(true);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 16000, channelCount: 1 } });
      mediaStreamRef.current = stream;
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      scriptProcessor.onaudioprocess = (event) => {
        if (!isRecordingRef.current || isMicMutedRef.current) return;
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
      setIsLoading(false);
      addMessage("status", t("recordingSpeakNow"));
    } catch (err) {
      setIsLoading(false);
      addMessage("error", "Mic Error");
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    isRecordingRef.current = false;
    if (scriptProcessorRef.current) scriptProcessorRef.current.disconnect();
    if (audioContextRef.current) audioContextRef.current.close();
    if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach(t => t.stop());
  };

  const sendTextQuery = async () => {
    if (!textQuestion.trim()) return;
    const userText = textQuestion;
    setTextQuestion("");
    setTextLoading(true);
    setTextMessages(p => [...p, { id: `u-${Date.now()}`, role: "user", text: userText, ts: new Date() }]);
    try {
      const response = await chatService.advisorChat({ message: userText, land_size_acres: landSize, include_sensor_data: true });
      setTextMessages(p => [...p, { id: `a-${Date.now()}`, role: "assistant", text: response.response, ts: new Date() }]);
    } catch (e) { setTextError("Chat failed"); } finally { setTextLoading(false); }
  };

  const addMessage = (type: Message["type"], text: string, language?: string) => {
    setMessages((prev) => [...prev, { type, text, timestamp: new Date(), language }]);
  };

  const getMessageColor = (type: Message["type"]) => {
    switch (type) {
      case "status": return "text-blue-600";
      case "transcription": return "text-green-600";
      case "ai_response": return "text-purple-600";
      case "error": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  return (
    <div className="space-y-4 p-4 max-w-5xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Leaf className="text-primary w-8 h-8" />
        <h1 className="text-2xl font-bold">{t("aiAdvisorHeading")}</h1>
      </div>

      <div className={`p-3 rounded-lg font-bold flex items-center gap-2 ${isConnected ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"}`}>
        <Radio className="w-5 h-5" />
        {isConnected ? t("connected") : t("disconnected")}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1 space-y-4">
          <Card>
            <CardHeader><CardTitle className="text-sm">{t("controls")}</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <Button onClick={isConnected ? disconnectWebSocket : connectWebSocket} disabled={isLoading} className="w-full" variant={isConnected ? "destructive" : "default"}>
                {isConnected ? t("disconnect") : t("connect")}
              </Button>
              <Button onClick={isRecording ? stopRecording : startRecording} disabled={!isConnected || isLoading} className="w-full" variant={isRecording ? "secondary" : "outline"}>
                {isRecording ? <MicOff className="mr-2 h-4 w-4" /> : <Mic className="mr-2 h-4 w-4" />}
                {isRecording ? t("stopRecording") : t("startRecording")}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-sm">{t("audioPlayback")}</CardTitle></CardHeader>
            <CardContent>
              <audio ref={audioPlayerRef} controls className="w-full h-10" />
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-3">
          <Card>
            <CardHeader><CardTitle>{t("messages")}</CardTitle></CardHeader>
            <CardContent className="h-[400px] overflow-y-auto space-y-2">
              {messages.map((msg, i) => (
                <div key={i} className={`p-2 rounded text-sm font-mono ${getMessageColor(msg.type)}`}>
                  {msg.text}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Text Chat Section */}
      <Card className="mt-6">
        <CardHeader><CardTitle className="text-sm">{t("aiChatAssistant")}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="h-48 overflow-y-auto border p-3 rounded space-y-2 bg-slate-50">
            {textMessages.map(m => (
              <div key={m.id} className={`p-2 rounded-lg max-w-[80%] ${m.role === 'user' ? 'bg-primary text-white ml-auto' : 'bg-white border mr-auto'}`}>
                {m.text}
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <Input value={textQuestion} onChange={e => setTextQuestion(e.target.value)} placeholder={t("typeQuestionPlaceholder")} />
            <Button onClick={sendTextQuery} disabled={textLoading} size="icon">
              {textLoading ? <Loader2 className="animate-spin" /> : <Send />}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, AlertCircle } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { chatService, type PublicChatResponse } from "@/services/chatService";

interface MessageBubble {
  id: string;
  type: "user" | "assistant";
  text: string;
  timestamp: Date;
}

export function PublicChat() {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<MessageBubble[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message to history
    const userMessage: MessageBubble = {
      id: `user-${Date.now()}`,
      type: "user",
      text: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setError(null);
    setShowLoginPrompt(false);

    try {
      setIsLoading(true);
      const response = await chatService.publicChat(inputValue);

      // Add assistant message
      const assistantMessage: MessageBubble = {
        id: `assistant-${Date.now()}`,
        type: "assistant",
        text: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Check if login is required
      if (response.requires_login) {
        setShowLoginPrompt(true);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get AI response. Please try again."
      );
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
    setShowLoginPrompt(false);
  };

  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader>
        <CardTitle>Ask AgriBot</CardTitle>
        <CardDescription>
          Get instant answers about agriculture and our services
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col gap-3 h-[400px] overflow-y-auto p-4 bg-muted/30 rounded-lg">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground text-center">
              <p>No messages yet. Ask me something!</p>
            </div>
          ) : (
            messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${
                  msg.type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.type === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {msg.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </motion.div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-secondary text-secondary-foreground px-4 py-2 rounded-lg">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
            </div>
          )}
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Login Prompt */}
        {showLoginPrompt && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              You need to login to access detailed agricultural advice
            </AlertDescription>
          </Alert>
        )}

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>

        {/* Clear Button */}
        {messages.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearChat}
            className="w-full"
          >
            Clear Chat
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

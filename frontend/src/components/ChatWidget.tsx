import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { fetchChatHistory, sendChatMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { useChatResults } from "../search/ChatResultsContext";
import "./ChatWidget.css";

interface ChatLine {
  role: "user" | "assistant";
  content: string;
  matchCount?: number;
}

const GREETING: ChatLine = {
  role: "assistant",
  content: "Hi! I'm the Campus Customs assistant. Ask me about our Yale gear.",
};

export default function ChatWidget() {
  const { user } = useAuth();
  const { setResults } = useChatResults();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState<ChatLine[]>([GREETING]);
  const bodyRef = useRef<HTMLDivElement>(null);

  // Keep the newest message in view -- without this, a reply that pushes
  // the panel's content past its fixed height is invisible until the user
  // manually scrolls, which was happening on every single exchange.
  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open]);

  // Logged-in customers get their saved conversation back whenever they
  // return; guests always start fresh, and signing out clears it.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING]);
      return;
    }
    let cancelled = false;
    fetchChatHistory(user.id, user.token)
      .then((history) => {
        if (cancelled) return;
        if (history.length === 0) {
          setMessages([GREETING]);
          return;
        }
        setMessages(
          history.map((item) => ({
            role: item.role,
            content: item.content,
            matchCount: item.products.length,
          }))
        );
      })
      .catch(() => {
        if (!cancelled) setMessages([GREETING]);
      });
    return () => {
      cancelled = true;
    };
  }, [user]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const response = await sendChatMessage(text, user?.token ?? null, location.pathname);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.message, matchCount: response.products.length },
      ]);

      // API contract: when the agent's reply includes structured product
      // matches, the website (not just the chat panel) updates to show
      // them as full product cards on the Products page.
      if (response.products.length > 0) {
        setResults(text, response.products);
        if (location.pathname !== "/products") {
          navigate("/products");
        }
      }
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Please try again.";
      setMessages((prev) => [...prev, { role: "assistant", content: `Sorry -- ${detail}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            <span>Campus Customs Assistant</span>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              &times;
            </button>
          </div>

          <div className="chat-panel-body" ref={bodyRef}>
            {messages.map((line, index) => (
              <div key={index} className={`chat-bubble chat-bubble-${line.role}`}>
                {line.content}
                {!!line.matchCount && (
                  <p className="chat-bubble-note">
                    Showing {line.matchCount} matching {line.matchCount === 1 ? "product" : "products"} on
                    the Products page.
                  </p>
                )}
              </div>
            ))}
            {sending && <div className="chat-bubble chat-bubble-assistant chat-bubble-pending">...</div>}
          </div>

          <form className="chat-panel-footer" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about products, sizes, colors..."
              disabled={sending}
            />
            <button type="submit" className="btn btn-primary" disabled={sending}>
              Send
            </button>
          </form>
        </div>
      )}

      <button className="chat-launcher" onClick={() => setOpen((v) => !v)} aria-label="Toggle chat">
        {open ? "Close" : "Chat"}
      </button>
    </div>
  );
}

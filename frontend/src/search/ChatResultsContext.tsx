import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";
import type { Product } from "../api/types";

/**
 * Shares the agent's structured product matches (the `products` array on
 * ChatReply -- the API contract between agent.py and the website) with the
 * Products page, so the page itself updates with full product cards when a
 * chat search happens, not just the small cards inside the chat panel.
 */
interface ChatResultsContextValue {
  results: Product[] | null;
  query: string | null;
  setResults: (query: string, results: Product[]) => void;
  clear: () => void;
}

const ChatResultsContext = createContext<ChatResultsContextValue | null>(null);

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResultsState] = useState<Product[] | null>(null);
  const [query, setQuery] = useState<string | null>(null);

  function setResults(nextQuery: string, nextResults: Product[]) {
    setQuery(nextQuery);
    setResultsState(nextResults);
  }

  function clear() {
    setQuery(null);
    setResultsState(null);
  }

  return (
    <ChatResultsContext.Provider value={{ results, query, setResults, clear }}>
      {children}
    </ChatResultsContext.Provider>
  );
}

export function useChatResults(): ChatResultsContextValue {
  const ctx = useContext(ChatResultsContext);
  if (!ctx) throw new Error("useChatResults must be used within ChatResultsProvider");
  return ctx;
}

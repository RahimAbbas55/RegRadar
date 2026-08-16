import { useState, useRef, useEffect } from "react";
import styles from "./ChatLayout.module.css";
import { CitationStamp } from "./CitationStamp";
import { ApiRequestError } from '../api/client';
import { streamQuery } from '../api/StreamClient';
import type { ChatMessage } from '../types/chat';

export function ChatLayout() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAwaitingFirstToken, setIsAwaitingFirstToken] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const exampleQuestions = [
    "Do I need to train my staff on money laundering?",
    "Who is responsible for outsourcing decisions?",
    "Which SYSC chapters apply to insurers?",
  ];

  function handleExampleClick(question: string) {
    setInputValue(question);
  }

  async function handleSend() {
    const trimmed = inputValue.trim();
    if (!trimmed || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    setIsAwaitingFirstToken(true);

    const assistantMessageId = crypto.randomUUID();
    let hasAddedAssistantMessage = false;

    try {
      for await (const event of streamQuery(trimmed)) {
        if (event.type === "sources") {
          setMessages((prev) => [
            ...prev,
            { id: assistantMessageId, role: "assistant", content: "", sources: event.sources },
          ]);
          hasAddedAssistantMessage = true;
          setIsAwaitingFirstToken(false);
        } else if (event.type === "token") {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId ? { ...m, content: m.content + event.text } : m
            )
          );
        } else if (event.type === "error") {
          if (!hasAddedAssistantMessage) {
            setMessages((prev) => [
              ...prev,
              { id: assistantMessageId, role: "assistant", content: event.message, isError: true },
            ]);
          }
        }
      }
    } catch (err) {
      const errorText =
        err instanceof ApiRequestError
          ? err.message
          : "Something went wrong. Please try again.";
      if (!hasAddedAssistantMessage) {
        setMessages((prev) => [
          ...prev,
          { id: assistantMessageId, role: "assistant", content: errorText, isError: true },
        ]);
      }
    } finally {
      setIsLoading(false);
      setIsAwaitingFirstToken(false);
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.wordmark}>RegRadar</h1>
        <span className={styles.tagline}>
          FCA Handbook compliance assistant
        </span>
      </header>

      <main className={styles.messageList}>
        {messages.length === 0 && !isLoading && (
          <div className={styles.emptyState}>
            <p className={styles.emptyStateText}>
              Ask a question about the FCA Handbook. Every answer cites the
              specific provision it's drawn from, and distinguishes binding
              Rules from Guidance.
            </p>
            <div className={styles.exampleQuestions}>
              {exampleQuestions.map((q) => (
                <button
                  key={q}
                  className={styles.exampleButton}
                  onClick={() => handleExampleClick(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) =>
          message.role === "user" ? (
            <div key={message.id} className={styles.messageUser}>
              <p>{message.content}</p>
            </div>
          ) : (
            <div
              key={message.id}
              className={
                message.isError ? styles.messageError : styles.messageAssistant
              }
            >
              <p>{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className={styles.citations}>
                  {message.sources.map((source) => (
                    <CitationStamp key={source.provision_id} source={source} />
                  ))}
                </div>
              )}
            </div>
          ),
        )}

        {isAwaitingFirstToken && (
          <div className={styles.messageAssistant}>
            <div className={styles.loadingIndicator}>
              <span className={styles.loadingDot} />
              <span className={styles.loadingDot} />
              <span className={styles.loadingDot} />
              <span className={styles.loadingText}>
                Searching the FCA Handbook…
              </span>
            </div>
          </div>
        )}
      </main>

      <footer className={styles.inputArea}>
        <input
          ref={inputRef}
          type="text"
          className={styles.input}
          placeholder="Ask a compliance question…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={isLoading}
        />
        <button
          className={styles.sendButton}
          onClick={handleSend}
          disabled={isLoading}
        >
          {isLoading ? "Asking…" : "Ask"}
        </button>
      </footer>
    </div>
  );
}
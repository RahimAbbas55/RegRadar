import { useState } from 'react';
import styles from './ChatLayout.module.css';
import { CitationStamp } from './CitationStamp';
import { submitQuery, ApiRequestError } from '../api/client';
import type { ChatMessage } from '../types/chat';

export function ChatLayout() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');

  async function handleSend() {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    try {
      const response = await submitQuery({ query: trimmed });
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorText = err instanceof ApiRequestError ? err.message : 'Something went wrong. Please try again.';
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: errorText,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.wordmark}>RegRadar</h1>
        <span className={styles.tagline}>FCA Handbook compliance assistant</span>
      </header>

      <main className={styles.messageList}>
        {messages.map((message) =>
          message.role === 'user' ? (
            <div key={message.id} className={styles.messageUser}>
              <p>{message.content}</p>
            </div>
          ) : (
            <div key={message.id} className={styles.messageAssistant}>
              <p>{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className={styles.citations}>
                  {message.sources.map((source) => (
                    <CitationStamp key={source.provision_id} source={source} />
                  ))}
                </div>
              )}
            </div>
          )
        )}
      </main>

      <footer className={styles.inputArea}>
        <input
          type="text"
          className={styles.input}
          placeholder="Ask a compliance question…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button className={styles.sendButton} onClick={handleSend}>
          Ask
        </button>
      </footer>
    </div>
  );
}
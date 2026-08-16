import styles from './ChatLayout.module.css';

export function ChatLayout() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.wordmark}>RegRadar</h1>
        <span className={styles.tagline}>FCA Handbook compliance assistant</span>
      </header>

      <main className={styles.messageList}>
        <div className={styles.messageUser}>
          <p>Do I need to train my staff on money laundering?</p>
        </div>

        <div className={styles.messageAssistant}>
          <p>
            Staff training on anti-money laundering is described as Guidance rather than a
            binding Rule — the FCA expects it as best practice, but it is not a strict legal
            requirement.
          </p>
        </div>
      </main>

      <footer className={styles.inputArea}>
        <input
          type="text"
          className={styles.input}
          placeholder="Ask a compliance question…"
        />
        <button className={styles.sendButton}>Ask</button>
      </footer>
    </div>
  );
}
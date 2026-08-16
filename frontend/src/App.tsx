function App() {
  return (
    <div style={{ padding: 'var(--space-8)' }}>
      <h1 style={{ fontFamily: 'var(--font-display)', color: 'var(--color-text-on-ink)' }}>
        RegRadar
      </h1>
      <p style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-accent)' }}>
        SYSC 3.2.6
      </p>
      <div
        style={{
          background: 'var(--color-paper)',
          color: 'var(--color-text-on-paper)',
          padding: 'var(--space-4)',
          borderRadius: 'var(--radius-md)',
          maxWidth: '400px',
        }}
      >
        Design tokens working — paper card on ink background.
      </div>
    </div>
  );
}

export default App;
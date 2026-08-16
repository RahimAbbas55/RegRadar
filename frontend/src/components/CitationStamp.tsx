import { useState } from 'react';
import styles from './CitationStamp.module.css';
import type { Source } from '../api/types';

interface CitationStampProps {
  source: Source;
}

export function CitationStamp({ source }: CitationStampProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const tagLabel = source.tag === 'R' ? 'Rule' : source.tag === 'G' ? 'Guidance' : 'Unknown';
  const tagClass = source.tag === 'R' ? styles.rule : source.tag === 'G' ? styles.guidance : styles.unknown;

  function toggleExpanded() {
    setIsExpanded((prev) => !prev);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault(); // prevent page scroll on Space
      toggleExpanded();
    }
  }

  return (
    <div className={styles.wrapper}>
      <div
        className={`${styles.stamp} ${tagClass}`}
        tabIndex={0}
        role="button"
        aria-expanded={isExpanded}
        aria-label={`${source.provision_id}, ${tagLabel}. ${isExpanded ? 'Collapse' : 'Expand'} to read full text.`}
        onClick={toggleExpanded}
        onKeyDown={handleKeyDown}
      >
        <span className={styles.provisionId}>{source.provision_id}</span>
        <span className={styles.tagLabel}>{tagLabel}</span>
      </div>

      {isExpanded && (
        <div className={styles.panel}>
          <p className={styles.panelText}>{source.text}</p>
        </div>
      )}
    </div>
  );
}
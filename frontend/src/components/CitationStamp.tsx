import styles from './CitationStamp.module.css';
import type { Source } from '../api/types';

interface CitationStampProps {
  source: Source;
}

export function CitationStamp({ source }: CitationStampProps) {
  const tagLabel = source.tag === 'R' ? 'Rule' : source.tag === 'G' ? 'Guidance' : 'Unknown';
  const tagClass = source.tag === 'R' ? styles.rule : source.tag === 'G' ? styles.guidance : styles.unknown;

  return (
    <div
      className={`${styles.stamp} ${tagClass}`}
      tabIndex={0}
      role="button"
      aria-label={`${source.provision_id}, ${tagLabel}. ${source.text}`}
      title={source.text}
    >
      <span className={styles.provisionId}>{source.provision_id}</span>
      <span className={styles.tagLabel}>{tagLabel}</span>
    </div>
  );
}
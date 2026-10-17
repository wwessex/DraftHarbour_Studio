import { useState, useEffect, useRef } from 'react';
import styles from './SaveStatus.module.css';

type SaveState = 'idle' | 'saving' | 'saved' | 'pending';

interface SaveStatusProps {
  isSaving: boolean;
  hasUnsavedChanges?: boolean;
}

export function SaveStatus({ isSaving, hasUnsavedChanges = false }: SaveStatusProps) {
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const timerRef = useRef<number | null>(null);
  const hadSaveRef = useRef(false);

  useEffect(() => {
    if (isSaving) {
      hadSaveRef.current = true;
      setSaveState('saving');
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    } else if (hasUnsavedChanges) {
      setSaveState('pending');
    } else if (hadSaveRef.current) {
      setSaveState('saved');
      timerRef.current = window.setTimeout(() => {
        setSaveState('idle');
        timerRef.current = null;
      }, 2500);
    }

    return () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, [isSaving, hasUnsavedChanges]);

  if (saveState === 'idle') return null;

  return (
    <span
      className={`${styles.saveStatus} ${styles[`saveStatus--${saveState}`]}`}
      role="status"
      aria-live="polite"
    >
      {saveState === 'saving' && (
        <>
          <span className={styles.saveDot} />
          <span>Saving</span>
        </>
      )}
      {saveState === 'saved' && (
        <>
          <span className="material-symbols-rounded" style={{ fontSize: '0.875rem' }}>check</span>
          <span>Saved</span>
        </>
      )}
      {saveState === 'pending' && (
        <>
          <span className={styles.saveDot} />
          <span>Unsaved changes</span>
        </>
      )}
    </span>
  );
}

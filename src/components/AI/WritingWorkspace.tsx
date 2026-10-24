import { lazy, Suspense, useEffect, useState } from 'react';
import type { WritingAction } from '@/lib/ai/writingActions';
import styles from './WritingWorkspace.module.css';
import { AISetup } from './AISetup';
import { AI_SETUP_CHANGED, AI_SETUP_MODE_KEY, getAISetupMode } from '@/lib/ai/setupPreferences';

const Composer = lazy(() => import('@/components/Modals/AIWritingModal').then(module => ({ default: module.AIWritingModal })));

/** Always-visible entry points; model code loads only after an explicit click. */
export function WritingWorkspace({ onConfigure }: { onConfigure?: () => void }) {
  const [request, setRequest] = useState<{ id: number; action: WritingAction } | null>(null);
  const [setup, setSetup] = useState(false);
  const [disabled, setDisabled] = useState(() => getAISetupMode() === 'later');
  const changed = () => { setRequest(null); setDisabled(getAISetupMode() === 'later'); };
  useEffect(() => {
    const changed = () => { setRequest(null); setDisabled(getAISetupMode() === 'later'); };
    const stored = (event: StorageEvent) => { if (event.key === AI_SETUP_MODE_KEY) changed(); };
    window.addEventListener(AI_SETUP_CHANGED, changed);
    window.addEventListener('storage', stored);
    return () => { window.removeEventListener(AI_SETUP_CHANGED, changed); window.removeEventListener('storage', stored); };
  }, []);
  return <aside className={styles.workspace} aria-label="AI writing workspace">
    <div className={styles.bar}>
      <button className={styles.action} onClick={() => { setRequest(null); setSetup(value => !value); }} aria-expanded={setup}>AI setup</button>
      {disabled && <span className={styles.hint}>AI is off. You can keep writing.</span>}
    </div>
    {setup && <AISetup onChanged={changed} onConfigure={onConfigure} />}
    {!request ? <div className={styles.bar}>
      <span className={styles.label}>AI writing</span>
      {(['write', 'rewrite', 'continue'] as const).map(action => <button key={action} type="button" disabled={disabled || setup} className={styles.action} onClick={() => setRequest({ id: Date.now(), action })}>
        {action === 'write' ? 'Write' : action === 'rewrite' ? 'Rewrite' : 'Continue'}
      </button>)}
    </div> : <Suspense fallback={<div className={styles.bar} role="status">Opening writing assistant…</div>}>
      <Composer open presentation="workspace" actionRequest={request} onClose={() => setRequest(null)} onConfigure={onConfigure ? () => { setRequest(null); onConfigure(); } : undefined} />
    </Suspense>}
  </aside>;
}

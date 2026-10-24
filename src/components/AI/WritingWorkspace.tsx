import { lazy, Suspense, useState } from 'react';
import type { WritingAction } from '@/lib/ai/writingActions';
import styles from './WritingWorkspace.module.css';
import { AISetup } from './AISetup';

const Composer = lazy(() => import('@/components/Modals/AIWritingModal').then(module => ({ default: module.AIWritingModal })));

/** Always-visible entry points; model code loads only after an explicit click. */
export function WritingWorkspace({ onConfigure }: { onConfigure?: () => void }) {
  const [request, setRequest] = useState<{ id: number; action: WritingAction } | null>(null);
  const [setup, setSetup] = useState(false);
  const [disabled, setDisabled] = useState(() => localStorage.getItem('draftharbour_ai_setup_mode_v1') === 'later');
  const changed = () => { setRequest(null); setDisabled(localStorage.getItem('draftharbour_ai_setup_mode_v1') === 'later'); };
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

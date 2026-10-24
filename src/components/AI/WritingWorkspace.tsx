import { lazy, Suspense, useState } from 'react';
import type { WritingAction } from '@/lib/ai/writingActions';
import styles from './WritingWorkspace.module.css';

const Composer = lazy(() => import('@/components/Modals/AIWritingModal').then(module => ({ default: module.AIWritingModal })));

/** Always-visible entry points; model code loads only after an explicit click. */
export function WritingWorkspace({ onConfigure }: { onConfigure?: () => void }) {
  const [request, setRequest] = useState<{ id: number; action: WritingAction } | null>(null);
  return <aside className={styles.workspace} aria-label="AI writing workspace">
    {!request ? <div className={styles.bar}>
      <span className={styles.label}>AI writing</span>
      {(['write', 'rewrite', 'continue'] as const).map(action => <button key={action} type="button" className={styles.action} onClick={() => setRequest({ id: Date.now(), action })}>
        {action === 'write' ? 'Write' : action === 'rewrite' ? 'Rewrite' : 'Continue'}
      </button>)}
    </div> : <Suspense fallback={<div className={styles.bar} role="status">Opening writing assistant…</div>}>
      <Composer open presentation="workspace" actionRequest={request} onClose={() => setRequest(null)} onConfigure={onConfigure ? () => { setRequest(null); onConfigure(); } : undefined} />
    </Suspense>}
  </aside>;
}

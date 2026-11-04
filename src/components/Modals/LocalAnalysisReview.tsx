import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/UI';
import { useApp } from '@/context/AppContext';
import { createLocalAIProvider, reviewManuscript } from '@/lib/ai/localReview';
import type { ReviewFinding } from '@/lib/ai/localReview';
import styles from './Modals.module.css';

export function LocalAnalysisReview({ open }: { open: boolean }) {
  const { state } = useApp();
  const [status, setStatus] = useState('');
  const [findings, setFindings] = useState<ReviewFinding[]>([]);
  const [overview, setOverview] = useState('');
  const [running, setRunning] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const projectId = state.novelId;
  useEffect(() => {
    controller.current?.abort();
    setRunning(false); setFindings([]); setOverview(''); setStatus('');
    return () => controller.current?.abort();
  }, [open, projectId]);
  const run = async () => {
    const abort = new AbortController(); controller.current = abort;
    setRunning(true); setFindings([]); setOverview(''); setStatus('Connecting to local model…');
    let provider;
    try {
      provider = await createLocalAIProvider();
      abort.signal.throwIfAborted();
      const result = await reviewManuscript(state.chapters, state.projectType, provider, abort.signal, (message, partial) => {
        if (!abort.signal.aborted) { setStatus(message); setFindings(partial); }
      });
      setOverview(result.overview);
      setStatus(`Review complete. ${result.emptyCount} empty sections skipped. Feedback refers to the manuscript at the start of this review.`);
    } catch (error) {
      if (!abort.signal.aborted) setStatus(error instanceof Error ? error.message : 'Local review failed.');
    } finally {
      provider?.destroy();
      if (controller.current === abort) setRunning(false);
    }
  };
  return <section className={styles.analysisCard} aria-label="Local AI manuscript analysis">
    <h4>Local AI — All {state.projectType === 'screenplay' ? 'Scenes' : 'Chapters'}</h4>
    <p>Get feedback on plot, characters, pacing and voice, with suggestions for revision. Manuscript text stays on this device. Suggestions do not change your draft.</p>
    <Button onClick={run} disabled={running || !state.chapters.length}>Review all {state.projectType === 'screenplay' ? 'scenes' : 'chapters'}</Button>
    {running && <Button onClick={() => { controller.current?.abort(); setStatus('Review cancelled. Partial feedback is shown below.'); }}>Cancel review</Button>}
    <p role="status">{status}</p>
    {overview && <div style={{ whiteSpace: 'pre-wrap' }}><h4>Overall feedback and suggestions</h4>{overview}</div>}
    {findings.map((finding, index) => <details key={index}><summary>{finding.title}</summary><p style={{ whiteSpace: 'pre-wrap' }}>{finding.feedback}</p></details>)}
  </section>;
}

import { useEffect, useRef, useState } from 'react';
import { useApp } from '@/context/AppContext';
import { createLocalAIProvider } from '@/lib/ai/localReview';
import { approvedChapterText, chatWithManuscript, type ChapterEditProposal } from '@/lib/ai/manuscriptChat';
import styles from './AIChatSidebar.module.css';

interface Message { role: 'You' | 'Assistant'; text: string; proposals?: ChapterEditProposal[]; warnings?: string[] }
export function AIChatSidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { state, applyAIChatEdit, setActiveChapter } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState('');
  const [requestEdits, setRequestEdits] = useState(false);
  const [applying, setApplying] = useState<string | null>(null);
  const applyingRef = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const latestState = useRef(state); latestState.current = state;
  useEffect(() => {
    controller.current?.abort(); setMessages([]); setPrompt(''); setError(''); setSending(false); setRequestEdits(false); setProgress('');
    return () => controller.current?.abort();
  }, [state.novelId]);
  const send = async () => {
    const question = prompt.trim();
    if (!question || sending || applyingRef.current) return;
    const abort = new AbortController(); controller.current = abort;
    setSending(true); setError(''); setProgress('Connecting to local model…');
    let provider;
    try {
      provider = await createLocalAIProvider();
      abort.signal.throwIfAborted();
      setMessages(previous => [...previous, { role: 'You', text: question }]); setPrompt('');
      const result = await chatWithManuscript({
        chapters: state.chapters, novelId: state.novelId, projectType: state.projectType, question,
        history: messages.slice(-6).map(message => `${message.role}: ${message.text}`).join('\n\n'),
        proposeEdits: requestEdits, provider, signal: abort.signal,
        progress: message => { if (!abort.signal.aborted) setProgress(message); },
      });
      abort.signal.throwIfAborted();
      setMessages(previous => [...previous, { role: 'Assistant', text: result.reply, proposals: result.proposals, warnings: result.warnings }]);
    } catch (cause) {
      if (!abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'Local AI chat failed.');
    } finally { provider?.destroy(); if (controller.current === abort) { setSending(false); setProgress(''); } }
  };
  const changeStatus = (id: string, status: ChapterEditProposal['status']) => setMessages(previous => previous.map(message => ({ ...message, proposals: message.proposals?.map(proposal => proposal.id === id ? { ...proposal, status } : proposal) })));
  const approve = async (proposal: ChapterEditProposal) => {
    if (applyingRef.current) return;
    applyingRef.current = true; setApplying(proposal.id); setError('');
    const projectId = state.novelId;
    try {
      const chapter = latestState.current.chapters.find(item => item.id === proposal.chapterId);
      let replacement;
      try { replacement = approvedChapterText(proposal, chapter); }
      catch (cause) { changeStatus(proposal.id, 'stale'); throw cause; }
      const saved = await applyAIChatEdit(proposal.chapterId, proposal.source, replacement);
      if (latestState.current.novelId !== projectId) return;
      changeStatus(proposal.id, 'accepted');
      if (!saved) setError('The approved change is in your draft, but saving failed. Keep this window open and retry saving.');
    } catch (cause) {
      if (latestState.current.novelId === projectId) setError(cause instanceof Error ? cause.message : 'Could not apply this proposal.');
    } finally { applyingRef.current = false; setApplying(null); }
  };
  if (!open) return null;
  return <aside className={styles.sidebar} aria-label="AI Chat">
    <header><h2>AI Chat</h2><button onClick={onClose} aria-label="Close AI Chat">×</button></header>
    <p>Local model · All {state.chapters.length} {state.projectType === 'screenplay' ? 'scenes' : 'chapters'}. Every section is read in parts. Edits require your approval.</p>
    <details><summary>Manuscript chapters</summary><ol>{[...state.chapters].sort((a, b) => a.order - b.order).map(chapter => <li key={chapter.id}><button onClick={() => setActiveChapter(chapter.id)}>{chapter.title}</button></li>)}</ol></details>
    <div className={styles.transcript} role="log" aria-label="Chat messages">
      {!messages.length && <p>Ask about any chapter, continuity or characters. Enable Request edit proposals to ask for manuscript changes.</p>}
      {messages.map((message, index) => <article key={index}>
        <strong>{message.role}</strong><p>{message.text}</p>
        {message.warnings?.map((warning, warningIndex) => <p key={warningIndex} role="status">{warning}</p>)}
        {message.proposals?.map(proposal => <section key={proposal.id} className={styles.proposal} aria-label={`Edit proposal for ${proposal.title}`}>
          <h3>{proposal.title} · {proposal.status}</h3>
          {proposal.edits.map((edit, editIndex) => <div key={editIndex}><p>{edit.rationale}</p><p><strong>Before</strong></p><pre>{edit.before}</pre><p><strong>After</strong></p><pre>{edit.after || '(delete this text)'}</pre></div>)}
          <p>A recovery snapshot is saved before applying approved edits.</p>
          <button disabled={proposal.status !== 'pending' || applying !== null || sending} onClick={() => { void approve(proposal); }}>{applying === proposal.id ? 'Applying…' : `Approve edits to ${proposal.title}`}</button>
          <button disabled={proposal.status !== 'pending' || applying !== null} onClick={() => changeStatus(proposal.id, 'rejected')}>Reject</button>
          <button onClick={() => setActiveChapter(proposal.chapterId)}>Open chapter</button>
        </section>)}
      </article>)}
    </div>
    {error && <p role="alert">{error}</p>}
    {sending && <p role="status">{progress}</p>}
    <form onSubmit={event => { event.preventDefault(); void send(); }}>
      <label className={styles.editToggle}><input type="checkbox" checked={requestEdits} disabled={sending} onChange={event => setRequestEdits(event.target.checked)} />Request edit proposals</label>
      <label htmlFor="local-chat-prompt">Message</label>
      <textarea id="local-chat-prompt" value={prompt} onChange={event => setPrompt(event.target.value)} rows={3} maxLength={2000} />
      <button type="submit" disabled={sending || applying !== null || !prompt.trim()}>Send</button>
      {sending && <button type="button" onClick={() => controller.current?.abort()}>Stop</button>}
      <button type="button" disabled={sending || applying !== null} onClick={() => { setMessages([]); setError(''); }}>New chat</button>
    </form>
  </aside>;
}

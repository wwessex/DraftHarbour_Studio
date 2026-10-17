import { useCallback, useEffect, useState } from 'react';
import { Button, useToast } from '@/components/UI';
import { createProjectBackup, getChapter, listProjectBackups, listTrash, restoreProjectBackup, restoreTrash } from '@/lib/storage';
import { listRecoveryDrafts, type RecoveryDraft } from '@/lib/recoveryJournal';
import { recoverDraftAsCopy } from '@/lib/recoverDraft';
import { downloadFile } from '@/lib/utils';
import type { ProjectBackup, TrashEntry } from '@/types';
import { useApp } from '@/context/AppContext';
import styles from './ProjectSafetyPanel.module.css';

export function ProjectSafetyPanel({ onRestored }: { onRestored: () => void }) {
  const { state, flushPendingSaves, loadNovelById, setActiveChapter } = useApp();
  const { showToast } = useToast();
  const [backups, setBackups] = useState<ProjectBackup[]>([]);
  const [trash, setTrash] = useState<TrashEntry[]>([]);
  const [drafts, setDrafts] = useState<RecoveryDraft[]>([]);
  const [savedText, setSavedText] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [backupName, setBackupName] = useState('');
  const refresh = useCallback(async () => {
    setBackups(await listProjectBackups(state.novelId));
    setTrash(await listTrash());
    const recovered = listRecoveryDrafts();
    setDrafts(recovered);
    setSavedText(Object.fromEntries(await Promise.all(recovered.map(async draft => [draft.key, (await getChapter(draft.chapter.id))?.content || '']))));
  }, [state.novelId]);
  useEffect(() => { void refresh().catch(() => showToast('Could not load safety copies', 'error')); }, [refresh, showToast]);
  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    try { await flushPendingSaves(); await action(); await refresh(); }
    catch (cause) { showToast(cause instanceof Error ? cause.message : 'Operation failed. Your original writing is unchanged.', 'error'); }
    finally { setBusy(false); }
  };
  const openCopy = async (novelId: string) => { await loadNovelById(novelId); onRestored(); };
  return <section aria-label="Backups, recovery and trash" className={styles.panel}>
    <h3>Recovery drafts</h3>
    <p>Compare unsaved writing from an earlier session. Recovery creates a new chapter and keeps the saved chapter.</p>
    {!drafts.length && <p>No unsaved drafts found.</p>}
    {drafts.map(draft => <article key={draft.key}>
      <h4>{draft.updates.title || draft.chapter.title}</h4>
      <p>{new Date(draft.savedAt).toLocaleString()}</p>
      <div className={styles.comparison}>
        <div><h5>Currently saved</h5><pre>{savedText[draft.key]}</pre></div>
        <div><h5>Recovery draft</h5><pre>{draft.updates.content ?? draft.chapter.content ?? ''}</pre></div>
      </div>
      <Button disabled={busy} onClick={() => void run(async () => {
        const recovered = await recoverDraftAsCopy(draft);
        await loadNovelById(recovered.novelId); setActiveChapter(recovered.chapterId); onRestored();
      })}>Recover as new chapter</Button>
    </article>)}
    <h3>Project backups</h3>
    <p>Automatic copies are made after one minute, then every five minutes while this project is open. The newest ten automatic copies are kept. Manual copies are retained. These copies share this device's storage; download a copy for protection against device loss.</p>
    <p>Includes manuscript, snapshots, comments, characters, world entries and story blueprint.</p>
    <label>Backup name (optional)<input value={backupName} onChange={e => setBackupName(e.target.value)} placeholder="Before restructuring" /></label>
    <Button disabled={busy} onClick={() => void run(async () => { await createProjectBackup(state.novelId, false, backupName); setBackupName(''); showToast('Verified backup created', 'success'); })}>Create verified backup</Button>
    {backups.map(backup => <article key={backup.id}>
      <p>{backup.label || (backup.automatic ? 'Automatic' : 'Manual')} · {new Date(backup.createdAt).toLocaleString()}</p>
      <Button disabled={busy} onClick={() => void run(async () => { await openCopy((await restoreProjectBackup(backup.id)).id); })}>Restore as project copy</Button>
      <Button variant="ghost" onClick={() => downloadFile(JSON.stringify(backup.data, null, 2), `${backup.data.project.title}-backup.json`)}>Download</Button>
    </article>)}
    {!backups.length && <p>No backups yet.</p>}
    <h3>Trash</h3>
    <p>Deleted chapters and projects can be restored as separate project copies.</p>
    {trash.map(entry => <article key={entry.id}>
      <p>{entry.title} · {entry.kind} · {new Date(entry.deletedAt).toLocaleString()}</p>
      <Button disabled={busy} onClick={() => void run(async () => { await openCopy((await restoreTrash(entry.id)).id); })}>Restore {entry.title}</Button>
    </article>)}
    {!trash.length && <p>Trash is empty.</p>}
  </section>;
}

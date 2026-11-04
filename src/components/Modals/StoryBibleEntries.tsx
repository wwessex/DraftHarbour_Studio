import { parseSceneFacts } from '@/lib/ai/bibleAccess';
import { useState } from 'react';
import { Button, Input, Textarea } from '@/components/UI';
import { Select } from '@/components/UI/Select';
import { useApp } from '@/context/AppContext';
import { downloadFile } from '@/lib/utils';
import { findEntityOccurrences } from '@/lib/entityOccurrences';
import { loadBibleEntries, newBibleEntry, persistBibleEntry, reviseBibleEntry, bibleMarkdown, importBibleEntries } from '@/lib/storyBibleEntries';
import { BIBLE_CATEGORIES, BIBLE_STATUSES, type BibleEntry } from '@/types/storyBible';
import styles from './StoryBibleEntries.module.css';

const labels: Record<string, string> = { character: 'Character', setting: 'Setting', event: 'Event', plotArc: 'Plot Arc', scene: 'Scene', theme: 'Theme / Motif', worldbuilding: 'Worldbuilding', research: 'Research Note', source: 'Source' };
const split = (text: string) => [...new Set(text.split(',').map(s => s.trim()).filter(Boolean))];

export function StoryBibleEntries() {
  const { state, setActiveChapter } = useApp();
  const [error, setError] = useState('');
  const [entries, setEntries] = useState<BibleEntry[]>(() => {
    try { return loadBibleEntries(state.novelId); } catch (e) { setError(String(e)); return []; }
  });
  const [selected, setSelected] = useState<string | null>(null);
  const [draft, setDraft] = useState<BibleEntry | null>(null);
  const [fields, setFields] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('all');
  const [archived, setArchived] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [message, setMessage] = useState('');
  const [importing, setImporting] = useState(false);
  const select = (entry: BibleEntry) => {
    setSelected(entry.id); setDraft(entry); setFields(Object.entries(entry.fields).map(([k, v]) => `${k}: ${v}`).join('\n')); setDirty(false); setMessage('');
  };
  const commit = (entry: BibleEntry) => {
    try {
      persistBibleEntry(entry); setEntries(loadBibleEntries(state.novelId)); select(entry); setError(''); setMessage('Saved locally');
    } catch (e) { setError(`Could not save: ${String(e)}`); }
  };
  const update = (change: Partial<BibleEntry>) => { if (draft) { setDraft({ ...draft, ...change }); setDirty(true); } };
  const save = () => {
    if (!draft || !draft.title.trim()) return;
    const pairs = fields.split('\n').filter(s => s.trim()).map(line => { const i = line.indexOf(':'); return i > 0 ? [line.slice(0, i).trim(), line.slice(i + 1).trim()] : null; });
    if (pairs.some(pair => !pair)) { setError('Use one custom field per line: Name: value'); return; }
    try { for (const condition of Object.values(draft.aiAccess?.conditions ?? {})) parseSceneFacts(condition); } catch (e) { setError(String(e)); return; }
    const current = entries.find(e => e.id === draft.id);
    const next = { ...draft, title: draft.title.trim(), fields: Object.fromEntries(pairs as string[][]) };
    commit(current ? reviseBibleEntry(current, next) : next);
  };
  const visible = entries.filter(e => e.archived === archived && (category === 'all' || e.category === category)
    && [e.title, e.body, ...e.aliases, ...e.tags, ...Object.values(e.fields)].join(' ').toLowerCase().includes(query.toLowerCase()));
  const mentions = draft ? findEntityOccurrences(state.chapters, [draft.title, ...draft.aliases]) : [];
  return <div className={styles.root}>
    <p>Keep story facts, ideas and research together. Only approved canon is used by AI. Existing character and world entries remain available in Characters & World.</p>
    {error && <p role="alert">{error}</p>}
    <div className={styles.toolbar}>
      <label>Import JSON<input aria-label="Import Story Bible JSON" type="file" accept=".json,application/json" disabled={dirty || importing} onChange={async e => {
        const file = e.target.files?.[0]; e.target.value = ''; if (!file) return;
        setImporting(true);
        try {
          if (file.size > 20 * 1024 * 1024) throw new Error('Story Bible imports must be under 20 MiB');
          importBibleEntries(JSON.parse(await file.text()), state.novelId);
          setEntries(loadBibleEntries(state.novelId)); setMessage('Imported as new entries'); setError('');
        } catch (err) { setError(String(err)); } finally { setImporting(false); }
      }} /></label>
      <Input aria-label="Search Story Bible" placeholder="Search titles, aliases, tags and text" value={query} onChange={e => setQuery(e.target.value)} />
      <Select aria-label="Filter entry type" value={category} onChange={e => setCategory(e.target.value)} options={[{ value: 'all', label: 'All types' }, ...BIBLE_CATEGORIES.map(value => ({ value, label: labels[value] }))]} />
      <label><input type="checkbox" checked={archived} onChange={e => setArchived(e.target.checked)} /> Archived</label>
      <Button disabled={dirty} onClick={() => { select(newBibleEntry(state.novelId, category === 'all' ? 'character' : category as BibleEntry['category'])); setDirty(true); }}>New entry</Button>
      <Button onClick={() => downloadFile(JSON.stringify({ bibleEntries: entries }, null, 2), 'story-bible.json', 'application/json')}>Export JSON</Button>
      <Button onClick={() => downloadFile(bibleMarkdown(entries), 'story-bible.md', 'text/markdown')}>Export Markdown</Button>
    </div>
    <div className={styles.layout}>
      <nav aria-label="Story Bible entries" className={styles.list}>
        {visible.length === 0 && <p>No entries found. Create an entry to begin.</p>}
        {visible.map(entry => <button key={entry.id} disabled={dirty} aria-current={selected === entry.id ? 'true' : undefined} onClick={() => select(entry)}><strong>{entry.title}</strong><small>{labels[entry.category]} · {entry.status}</small></button>)}
      </nav>
      {draft ? <section className={styles.editor} aria-label="Entry editor">
        <label>Title<Input value={draft.title} onChange={e => update({ title: e.target.value })} /></label>
        <div className={styles.toolbar}>
          <label>Type<Select value={draft.category} onChange={e => update({ category: e.target.value as BibleEntry['category'] })} options={BIBLE_CATEGORIES.map(value => ({ value, label: labels[value] }))} /></label>
          <label>Canon status<Select value={draft.status} onChange={e => update({ status: e.target.value as BibleEntry['status'] })} options={BIBLE_STATUSES.map(value => ({ value, label: value.replaceAll('_', ' ') }))} /></label>
        </div>
        <label>Aliases<Input value={draft.aliases.join(',')} onChange={e => update({ aliases: e.target.value.split(',') })} onBlur={() => update({ aliases: split(draft.aliases.join(',')) })} /></label>
        <label>Tags<Input value={draft.tags.join(',')} onChange={e => update({ tags: e.target.value.split(',') })} onBlur={() => update({ tags: split(draft.tags.join(',')) })} /></label>
        <label>Notes<Textarea rows={7} value={draft.body} onChange={e => update({ body: e.target.value })} /></label>
        <label>Custom fields<Textarea placeholder="Goal: Find the missing ship" value={fields} onChange={e => { const names = e.target.value.split('\n').map(line => line.split(':')[0].trim()).filter(Boolean); const oldNames = fields.split('\n').map(line => line.split(':')[0].trim()); update({ aiAccess: { ...draft.aiAccess, hiddenFields: [...new Set([...(draft.aiAccess?.hiddenFields ?? []), ...names.filter(name => !oldNames.includes(name)).map(name => `field:${name}`)])] } }); setFields(e.target.value); setDirty(true); }} /></label>
        <details><summary>AI reference access</summary>
          <p>These controls affect structured Bible references. Facts already written in your manuscript or other cards remain visible there. New or renamed custom fields start hidden until enabled.</p>
          <label><input type="checkbox" checked={!draft.aiAccess?.hidden} onChange={e => update({ aiAccess: { ...draft.aiAccess, hidden: !e.target.checked } })} /> Allow AI to reference this entry</label>
          {[['body', 'Notes'], ['aliases', 'Aliases'], ['validity', 'Validity notes'], ...fields.split('\n').filter(line => line.indexOf(':') > 0).map(line => { const name = line.slice(0, line.indexOf(':')).trim(); return [`field:${name}`, name]; })].map(([key, label]) => <div key={key}>
            <label><input type="checkbox" checked={!draft.aiAccess?.hiddenFields?.includes(key)} onChange={e => update({ aiAccess: { ...draft.aiAccess, hiddenFields: e.target.checked ? (draft.aiAccess?.hiddenFields ?? []).filter(field => field !== key) : [...(draft.aiAccess?.hiddenFields ?? []), key] } })} /> Allow {label}</label>
            <label>Only use {label} when<Input placeholder="e.g. form=human, timeline=before" value={draft.aiAccess?.conditions?.[key] ?? ''} onChange={e => update({ aiAccess: { ...draft.aiAccess, conditions: { ...draft.aiAccess?.conditions, [key]: e.target.value } } })} /></label>
          </div>)}
          <p>Conditions require matching Scene facts in the writing assistant. Missing facts exclude the field; validity notes are never interpreted automatically.</p>
        </details>
        <label>Provenance / evidence<Input placeholder="Manual, chapter reference, or source and locator" value={draft.provenance} onChange={e => update({ provenance: e.target.value })} /></label>
        <div className={styles.toolbar}>
          <label>Valid from<Input placeholder="e.g. Chapter 2" value={draft.validFrom} onChange={e => update({ validFrom: e.target.value })} /></label>
          <label>Valid until<Input placeholder="e.g. Chapter 17" value={draft.validTo} onChange={e => update({ validTo: e.target.value })} /></label>
        </div>
        <details><summary>Linked entries ({draft.linkedEntryIds.length})</summary>{entries.filter(e => e.id !== draft.id && !e.archived).map(e => <label key={e.id}><input type="checkbox" checked={draft.linkedEntryIds.includes(e.id)} onChange={ev => update({ linkedEntryIds: ev.target.checked ? [...draft.linkedEntryIds, e.id] : draft.linkedEntryIds.filter(id => id !== e.id) })} /> {e.title}</label>)}</details>
        <details><summary>Backlinks</summary>{entries.filter(e => !e.archived && e.linkedEntryIds.includes(draft.id)).map(e => <Button key={e.id} disabled={dirty} onClick={() => select(e)}>{e.title}</Button>)}</details>
        <details><summary>Manuscript mentions ({mentions.length})</summary>{mentions.map(m => <Button key={`${m.chapterId}:${m.name}:${m.excerpt}`} onClick={() => setActiveChapter(m.chapterId)}>{m.chapterTitle}: {m.excerpt}</Button>)}</details>
        <div className={styles.toolbar}>
          <Button disabled={!dirty || !draft.title.trim()} onClick={save}>Save entry</Button>
          {dirty && <Button onClick={() => { const current = entries.find(e => e.id === draft.id); if (current) select(current); else { setDraft(null); setDirty(false); } }}>Discard edits</Button>}
          {entries.some(e => e.id === draft.id) && <Button disabled={dirty} onClick={() => commit(reviseBibleEntry(draft, { ...draft, archived: !draft.archived }, draft.archived ? 'Unarchived' : 'Archived'))}>{draft.archived ? 'Unarchive entry' : 'Archive entry'}</Button>}
          <span role="status">{dirty ? 'Unsaved edits — save or discard before switching entries.' : message}</span>
        </div>
        <details><summary>Version history ({draft.revisions.length})</summary>{[...draft.revisions].reverse().map(r => <div key={r.id}><p>{new Date(r.createdAt).toLocaleString()} · {r.reason} · {r.state.title} ({r.state.status})</p><pre>{r.state.body}</pre><Button disabled={dirty} onClick={() => commit(reviseBibleEntry(draft, r.state, 'Restored revision'))}>Restore this version</Button></div>)}</details>
      </section> : <p>Select an entry or create a new one. Everything can be edited offline.</p>}
    </div>
  </div>;
}

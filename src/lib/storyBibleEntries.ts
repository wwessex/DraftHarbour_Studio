import { generateId } from '@/lib/utils';
import type { BibleEntry, BibleEntryState } from '@/types/storyBible';
import { BIBLE_CATEGORIES, BIBLE_STATUSES, BIBLE_TEMPLATES } from '@/types/storyBible';

export const BIBLE_ENTRIES_KEY = 'draftharbour_bible_entries';
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.every(item => typeof item === 'string');
function validAccess(value: unknown): boolean {
  if (value === undefined) return true;
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const a = value as NonNullable<BibleEntryState['aiAccess']>;
  return (a.hidden === undefined || typeof a.hidden === 'boolean') && (a.hiddenFields === undefined || strings(a.hiddenFields))
    && (a.conditions === undefined || (!!a.conditions && typeof a.conditions === 'object' && !Array.isArray(a.conditions) && Object.values(a.conditions).every(v => typeof v === 'string')));
}
function isState(value: unknown): value is BibleEntryState {
  if (!value || typeof value !== 'object') return false;
  const s = value as BibleEntryState;
  return validAccess(s.aiAccess) && typeof s.title === 'string' && BIBLE_CATEGORIES.includes(s.category) && BIBLE_STATUSES.includes(s.status)
    && typeof s.body === 'string' && strings(s.aliases) && strings(s.tags) && strings(s.linkedEntryIds)
    && !!s.fields && typeof s.fields === 'object' && !Array.isArray(s.fields) && Object.values(s.fields).every(v => typeof v === 'string')
    && typeof s.provenance === 'string' && typeof s.validFrom === 'string' && typeof s.validTo === 'string' && typeof s.archived === 'boolean';
}
export function isBibleEntry(value: unknown): value is BibleEntry {
  if (!isState(value)) return false;
  const e = value as BibleEntry;
  return typeof e.id === 'string' && typeof e.novelId === 'string' && Number.isFinite(e.createdAt) && Number.isFinite(e.updatedAt)
    && Array.isArray(e.revisions) && e.revisions.every(r => r && typeof r.id === 'string' && Number.isFinite(r.createdAt) && typeof r.reason === 'string' && isState(r.state));
}
export function readBibleEntries(): BibleEntry[] {
  const raw = localStorage.getItem(BIBLE_ENTRIES_KEY);
  if (!raw) return [];
  const parsed: unknown = JSON.parse(raw);
  // Never overwrite a damaged collection by treating it as an empty one.
  if (!Array.isArray(parsed) || !parsed.every(isBibleEntry)) throw new Error('Story Bible data could not be read. Export a backup before repairing local storage.');
  return parsed;
}
export function loadBibleEntries(novelId: string): BibleEntry[] {
  return readBibleEntries().filter(e => e.novelId === novelId);
}
export function persistBibleEntry(entry: BibleEntry): void {
  const all = readBibleEntries();
  localStorage.setItem(BIBLE_ENTRIES_KEY, JSON.stringify([...all.filter(e => e.id !== entry.id), entry]));
}
export function newBibleEntry(novelId: string, category: BibleEntry['category'] = 'character'): BibleEntry {
  return { id: generateId(), novelId, createdAt: Date.now(), updatedAt: Date.now(), title: 'Untitled entry', category,
    status: category === 'research' || category === 'source' ? 'research' : 'draft', body: '', aliases: [], tags: [], linkedEntryIds: [], fields: { ...BIBLE_TEMPLATES[category] }, provenance: 'Manual', validFrom: '', validTo: '', archived: false, revisions: [] };
}
export function reviseBibleEntry(entry: BibleEntry, state: BibleEntryState, reason = 'Edited'): BibleEntry {
  const { aiAccess, title, category, status, body, aliases, tags, linkedEntryIds, fields, provenance, validFrom, validTo, archived, revisions } = entry;
  const previous = { aiAccess, title, category, status, body, aliases, tags, linkedEntryIds, fields, provenance, validFrom, validTo, archived };
  return { ...entry, ...state, updatedAt: Date.now(), revisions: [...revisions, { id: generateId(), createdAt: Date.now(), reason, state: previous }] };
}
export function bibleMarkdown(entries: BibleEntry[]): string {
  return entries.filter(e => !e.archived).map(e => `# ${e.title}\n\nType: ${e.category}\nStatus: ${e.status}\nAliases: ${e.aliases.join(', ')}\nTags: ${e.tags.join(', ')}\nValid: ${e.validFrom || 'Unspecified'} → ${e.validTo || 'Unspecified'}\nProvenance: ${e.provenance}\n\n${e.body}\n\n${Object.entries(e.fields).map(([key, value]) => `${key}: ${value}`).join('\n')}\n\nLinks: ${e.linkedEntryIds.map(id => entries.find(e => e.id === id)?.title ?? id).join(', ')}`).join('\n\n---\n\n');
}

/** Import as new project-owned identities; one storage write keeps the collection intact on quota failure. */
export function importBibleEntries(value: unknown, novelId: string): BibleEntry[] {
  if (!value || typeof value !== 'object' || !('bibleEntries' in value) || !Array.isArray(value.bibleEntries) || !value.bibleEntries.every(isBibleEntry)) throw new Error('Invalid Story Bible JSON');
  const source: BibleEntry[] = value.bibleEntries;
  if (new Set(source.map(e => e.id)).size !== source.length) throw new Error('Duplicate Story Bible IDs');
  const ids = new Map(source.map(e => [e.id, generateId()]));
  const state = (s: BibleEntryState): BibleEntryState => ({ ...s, linkedEntryIds: s.linkedEntryIds.filter(id => ids.has(id)).map(id => ids.get(id)!) });
  const entries = source.map(e => ({ ...e, ...state(e), id: ids.get(e.id)!, novelId,
    revisions: e.revisions.map(r => ({ ...r, id: generateId(), state: state(r.state) })) }));
  localStorage.setItem(BIBLE_ENTRIES_KEY, JSON.stringify([...readBibleEntries(), ...entries]));
  return entries;
}

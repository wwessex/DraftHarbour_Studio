import type { BibleEntry, BibleEntryState } from '@/types/storyBible';

/** Scene facts are explicit request inputs, never inferred from prose or validity notes. */
export function parseSceneFacts(text: string): Record<string, string> {
  const facts: Record<string, string> = Object.create(null) as Record<string, string>;
  for (const item of text.split(',')) {
    if (!item.trim()) continue;
    const pair = item.split('=');
    if (pair.length !== 2 || !pair[0].trim() || !pair[1].trim() || Object.hasOwn(facts, pair[0].trim())) {
      throw new Error('Use unique scene facts as name=value, separated by commas.');
    }
    facts[pair[0].trim()] = pair[1].trim();
  }
  return facts;
}
export function bibleFieldVisible(state: BibleEntryState, field: string, scene: Record<string, string> = {}): boolean {
  if (state.aiAccess?.hidden || state.aiAccess?.hiddenFields?.includes(field)) return false;
  try {
    return Object.entries(parseSceneFacts(state.aiAccess?.conditions?.[field] ?? '')).every(([key, value]) => Object.hasOwn(scene, key) && scene[key] === value);
  } catch { return false; }
}
export function inferenceBibleEntry(entry: BibleEntry, scene: Record<string, string> = {}): BibleEntry | null {
  if (entry.archived || entry.status !== 'canon' || entry.aiAccess?.hidden) return null;
  return { ...entry, body: bibleFieldVisible(entry, 'body', scene) ? entry.body : '',
    aliases: bibleFieldVisible(entry, 'aliases', scene) ? entry.aliases : [],
    fields: Object.fromEntries(Object.entries(entry.fields).filter(([key]) => bibleFieldVisible(entry, `field:${key}`, scene))),
    validFrom: bibleFieldVisible(entry, 'validity', scene) ? entry.validFrom : '',
    validTo: bibleFieldVisible(entry, 'validity', scene) ? entry.validTo : '',
    provenance: '', tags: [], linkedEntryIds: [], revisions: [], aiAccess: undefined };
}
/** Structured canon overrides matching legacy cards even when hidden or archived. */
export function controlledBibleNames(entries: BibleEntry[]): Set<string> {
  return new Set(entries.filter(e => e.status === 'canon' || e.aiAccess?.hidden).flatMap(e => [e.title, ...e.aliases]).map(name => name.trim().toLowerCase()));
}
export function referenceMatch(query: string, name: string): boolean {
  if (!name.trim()) return false;
  const escaped = name.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(?<![\\p{L}\\p{N}_])${escaped}(?![\\p{L}\\p{N}_])`, 'iu').test(query);
}

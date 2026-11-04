/** Portable author-controlled Story Bible. Dates use epoch milliseconds. */
export const BIBLE_CATEGORIES = ['character', 'setting', 'event', 'plotArc', 'scene', 'theme', 'worldbuilding', 'research', 'source'] as const;
export const BIBLE_STATUSES = ['idea', 'draft', 'canon', 'disputed', 'superseded', 'deprecated', 'research', 'ai_suggestion'] as const;
export interface BibleEntryState {
  /** Optional portable inference policy. Missing policy preserves existing behaviour. */
  aiAccess?: { hidden?: boolean; hiddenFields?: string[]; conditions?: Record<string, string> };
  title: string;
  category: typeof BIBLE_CATEGORIES[number];
  status: typeof BIBLE_STATUSES[number];
  body: string;
  aliases: string[];
  tags: string[];
  linkedEntryIds: string[];
  fields: Record<string, string>;
  provenance: string;
  validFrom: string;
  validTo: string;
  archived: boolean;
}
export interface BibleRevision {
  id: string;
  createdAt: number;
  reason: string;
  state: BibleEntryState;
}
export interface BibleEntry extends BibleEntryState {
  id: string;
  novelId: string;
  createdAt: number;
  updatedAt: number;
  revisions: BibleRevision[];
}

export const BIBLE_TEMPLATES: Partial<Record<BibleEntry['category'], Record<string, string>>> = {
  character: { Goal: '', Fear: '', Voice: '', Backstory: '' },
  setting: { Atmosphere: '', Geography: '', Ownership: '' },
  event: { Start: '', End: '', Participants: '', 'Narrative order': '', 'Chronological order': '' },
  plotArc: { Goal: '', Stakes: '', Setup: '', Climax: '', Resolution: '' },
  scene: { POV: '', Location: '', Purpose: '', Outcome: '' },
  theme: { Question: '', Motif: '' },
  worldbuilding: { Rules: '', Exceptions: '' },
  research: { Question: '', Sources: '' },
  source: { Creator: '', Publisher: '', URL: '', Locator: '', Rights: '' },
};

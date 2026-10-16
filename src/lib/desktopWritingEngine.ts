import type { Chapter } from '@/types';
import { editorToPlainText } from '@/lib/utils';
import {
  buildChapterSearchIndex,
  findChapterContentMatches,
  type ChapterSearchResult,
} from '@/lib/search';
import { getTauriRuntime } from '@/lib/tauriRuntime';

interface NativeSearchResult {
  chapterId: string;
  chapterTitle: string;
  snippet: string;
  matchRange: { start: number; end: number };
  score: number;
}

export interface NativeManuscriptStatistics {
  documents: Array<{
    id: string;
    words: number;
    sentences: number;
    paragraphs: number;
    characters: number;
  }>;
  totalWords: number;
  totalSentences: number;
  totalParagraphs: number;
  totalCharacters: number;
}

function toNativeDocuments(chapters: Chapter[]) {
  return chapters.map((chapter, index) => ({
    id: chapter.id,
    title: chapter.title?.trim() || `Chapter ${index + 1}`,
    plainText: editorToPlainText(chapter.content),
  }));
}

/**
 * Runs whole-manuscript search off the UI thread in the desktop app. Browser and
 * mobile builds keep the established TypeScript implementation as a fallback.
 */
export async function searchManuscript(
  chapters: Chapter[],
  query: string,
  maxResults = 30,
): Promise<ChapterSearchResult[]> {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) return [];

  const runtime = await getTauriRuntime();
  if (!runtime) {
    return findChapterContentMatches(buildChapterSearchIndex(chapters), trimmedQuery, maxResults);
  }

  let results: NativeSearchResult[];
  try {
    results = await runtime.invoke<NativeSearchResult[]>('search_manuscript', {
      documents: toNativeDocuments(chapters),
      query: trimmedQuery,
      maxResults,
    });
  } catch (error) {
    console.warn('Native manuscript search unavailable; using the cross-platform engine.', error);
    return findChapterContentMatches(buildChapterSearchIndex(chapters), trimmedQuery, maxResults);
  }

  return results.map(result => ({
    chapterId: result.chapterId,
    chapterTitle: result.chapterTitle,
    snippet: result.snippet,
    match: result.matchRange,
    score: result.score,
  }));
}

export async function analyzeManuscript(chapters: Chapter[]): Promise<NativeManuscriptStatistics | null> {
  const runtime = await getTauriRuntime();
  if (!runtime) return null;
  return runtime.invoke<NativeManuscriptStatistics>('analyze_manuscript', {
    documents: toNativeDocuments(chapters),
  });
}

export async function validateBackupWithNativeEngine(contents: string): Promise<boolean> {
  const runtime = await getTauriRuntime();
  if (!runtime) return false;
  await runtime.invoke('validate_backup', { contents });
  return true;
}

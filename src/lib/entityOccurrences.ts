import type { Chapter } from '@/types';
import { editorToPlainText } from '@/lib/utils';

export function findEntityOccurrences(chapters: Chapter[], names: string[], limit = 100) {
  const terms = [...new Set(names.map(name => name.trim()).filter(Boolean))].sort((a, b) => b.length - a.length);
  if (!terms.length) return [];
  const escaped = terms.map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = new RegExp(`(^|[^\\p{L}\\p{N}_])(${escaped.join('|')})(?=$|[^\\p{L}\\p{N}_])`, 'giu');
  const results: Array<{ chapterId: string; chapterTitle: string; excerpt: string; name: string }> = [];
  for (const chapter of chapters) {
    const text = editorToPlainText(chapter.content);
    pattern.lastIndex = 0;
    for (const match of text.matchAll(pattern)) {
      const start = match.index + match[1].length;
      results.push({ chapterId: chapter.id, chapterTitle: chapter.title, name: match[2], excerpt: text.slice(Math.max(0, start - 60), start + match[2].length + 80) });
      if (results.length >= limit) return results;
    }
  }
  return results;
}

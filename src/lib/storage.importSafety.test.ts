/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import JSZip from 'jszip';
import { beforeEach, describe, expect, it } from 'vitest';
import type { BackupDataV3, DhprojData } from '@/types';
import { addChapter, createChapter, createNovel, db, getChapters, getCommentThreads, getSnapshots, importBackup, importDhproj, upsertCommentThread } from './storage';

const richDoc = { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Legacy prose', marks: [{ type: 'bold' }] }] }] };

function backup(): BackupDataV3 {
  return {
    version: 3, projectType: 'book', exportedAt: 1,
    project: { id: 'source', title: 'Imported', updatedAt: 1 },
    sections: [{ ...createChapter('source', 0), id: 'source-chapter', content: richDoc as unknown as string,
      sync: { providerRevisionIds: {}, lastSyncedContent: richDoc as unknown as string } }],
    snapshots: [{ id: 'source-snapshot', chapterId: 'source-chapter', createdAt: 1, doc: richDoc as unknown as string }],
  };
}

async function projectFile(data: BackupDataV3) {
  const zip = new JSZip();
  zip.file('project.json', JSON.stringify({ ...data, manifest: { format: 'dhproj', version: 1 } } as unknown as DhprojData));
  return new File([await zip.generateAsync({ type: 'uint8array' })], 'test.dhproj');
}

beforeEach(async () => {
  await db.transaction('rw', [db.novels, db.chapters, db.snapshots], async () => {
    await db.snapshots.clear();
    await db.chapters.clear();
    await db.novels.clear();
  });
});

describe.each(['backup', 'dhproj'] as const)('%s import safety', format => {
  const restore = async (data: BackupDataV3) => format === 'backup' ? importBackup(data) : importDhproj(await projectFile(data));

  it('converts legacy rich text in chapters, sync baselines and snapshots', async () => {
    const novel = await restore(backup());
    const [chapter] = await getChapters(novel.id);
    expect(chapter.content).toBe('**Legacy prose**');
    expect(chapter.sync?.lastSyncedContent).toBe('**Legacy prose**');
    expect((await getSnapshots(chapter.id))[0].doc).toBe('**Legacy prose**');
  });

  it('rejects duplicate chapter IDs before writing any imported data', async () => {
    const data = backup();
    data.sections.push({ ...data.sections[0] });
    await expect(restore(data)).rejects.toThrow('unique');
    expect(await db.novels.count()).toBe(0);
    expect(await db.chapters.count()).toBe(0);
  });

  it('rejects foreign chapter references without altering existing manuscripts or comments', async () => {
    const existing = await createNovel('Keep me');
    const chapter = createChapter(existing.id, 0);
    chapter.content = 'Original manuscript';
    await addChapter(chapter);
    const thread = { id: 'thread', chapterId: chapter.id, anchor: { from: 0, to: 5, length: 5 }, resolved: false, createdAt: 1, updatedAt: 1, comments: [] };
    upsertCommentThread(thread);
    const data = backup();
    data.commentThreads = [{ ...thread, comments: [{ id: 'changed', text: 'Overwrite', author: 'Other', createdAt: 2 }] }];
    await expect(restore(data)).rejects.toThrow('unknown chapter');
    expect(await db.novels.count()).toBe(1);
    expect((await getChapters(existing.id))[0].content).toBe('Original manuscript');
    expect(getCommentThreads(chapter.id)).toEqual([thread]);
  });
});

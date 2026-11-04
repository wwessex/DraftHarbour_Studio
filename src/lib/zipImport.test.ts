import JSZip from 'jszip';
import { expect, it } from 'vitest';
import { createZipTextReader } from './zipImport';

it('bounds actual expanded bytes cumulatively and preserves UTF-8 text', async () => {
  const original = new JSZip();
  original.file('one', 'hello 🌊');
  original.file('two', 'A'.repeat(64 * 1024));
  const archive = await JSZip.loadAsync(await original.generateAsync({ type: 'uint8array', compression: 'DEFLATE' }));
  const read = createZipTextReader(64 * 1024);
  await expect(read(archive.file('one')!)).resolves.toBe('hello 🌊');
  await expect(read(archive.file('two')!)).rejects.toThrow('expanded import size limit');
  await expect(createZipTextReader(64 * 1024)(archive.file('two')!)).resolves.toHaveLength(64 * 1024);
});

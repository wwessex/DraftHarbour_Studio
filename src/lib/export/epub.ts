import type { Chapter } from '@/types';
import { markdownToBlocks } from '@/lib/editor/markdownParser';
import { downloadFile, generateId } from '@/lib/utils';

const xml = (value: string) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

export async function buildEpub(chapters: Chapter[], title: string, author = '', language = 'en') {
  if (!chapters.length) throw new Error('Add a chapter before exporting EPUB.');
  const JSZip = (await import('jszip')).default;
  const zip = new JSZip();
  zip.file('mimetype', 'application/epub+zip', { compression: 'STORE' });
  zip.file('META-INF/container.xml', '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>');
  zip.file('EPUB/style.css', 'body{font-family:serif;line-height:1.5}p{margin:0 0 .8em}h1,h2,h3{break-after:avoid}pre{white-space:pre-wrap}.underline{text-decoration:underline}');
  for (const [index, chapter] of chapters.entries()) {
    const body = markdownToBlocks(chapter.content || '').map(block => {
      const text = block.runs.map(run => {
        let content = xml(run.text).replace(/\n/g, '<br/>');
        if (run.bold) content = `<strong>${content}</strong>`;
        if (run.italic) content = `<em>${content}</em>`;
        if (run.underline) content = `<span class="underline">${content}</span>`;
        if (run.strike) content = `<s>${content}</s>`;
        return content;
      }).join('');
      switch (block.type) {
        case 'heading': { const level = Math.min(6, Math.max(2, block.level || 2)); return `<h${level}>${text}</h${level}>`; }
        case 'blockquote': return `<blockquote><p>${text}</p></blockquote>`;
        case 'bulletItem': return `<ul><li>${text}</li></ul>`;
        case 'orderedItem': return `<ol><li>${text}</li></ol>`;
        case 'codeBlock': return `<pre>${xml(block.text)}</pre>`;
        case 'horizontalRule': return '<hr/>';
        case 'image': return `<p>[Image omitted from text-only EPUB: ${xml(block.text)}]</p>`;
        default: return `<p>${text || '<br/>'}</p>`;
      }
    }).join('\n');
    zip.file(`EPUB/chapter-${index + 1}.xhtml`, `<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="${xml(language)}"><head><title>${xml(chapter.title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body><h1>${xml(chapter.title)}</h1>${body}</body></html>`);
  }
  const nav = chapters.map((chapter, index) => `<li><a href="chapter-${index + 1}.xhtml">${xml(chapter.title)}</a></li>`).join('');
  zip.file('EPUB/nav.xhtml', `<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="${xml(language)}"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol>${nav}</ol></nav></body></html>`);
  const manifest = chapters.map((_, index) => `<item id="ch${index + 1}" href="chapter-${index + 1}.xhtml" media-type="application/xhtml+xml"/>`).join('');
  const spine = chapters.map((_, index) => `<itemref idref="ch${index + 1}"/>`).join('');
  zip.file('EPUB/package.opf', `<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:uuid:${generateId()}</dc:identifier><dc:title>${xml(title)}</dc:title><dc:language>${xml(language)}</dc:language>${author ? `<dc:creator>${xml(author)}</dc:creator>` : ''}<meta property="dcterms:modified">${new Date().toISOString().replace(/\.\d+Z$/, 'Z')}</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="style.css" media-type="text/css"/>${manifest}</manifest><spine>${spine}</spine></package>`);
  return zip.generateAsync({ type: 'uint8array', compression: 'DEFLATE' });
}

export async function exportToEpub(chapters: Chapter[], title: string, author = '', language = 'en') {
  const bytes = await buildEpub(chapters, title, author, language);
  downloadFile(new Blob([bytes], { type: 'application/epub+zip' }), `${title}.epub`);
}

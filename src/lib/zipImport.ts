import type JSZip from 'jszip';

export const MAX_ZIP_IMPORT_BYTES = 100 * 1024 * 1024;

interface ZipByteStream {
  on(event: 'data', listener: (chunk: Uint8Array) => void): ZipByteStream;
  on(event: 'error', listener: (error: Error) => void): ZipByteStream;
  on(event: 'end', listener: () => void): ZipByteStream;
  pause(): ZipByteStream;
  resume(): ZipByteStream;
}

/** A single expanded-byte budget shared by all entries read from an archive. */
export function createZipTextReader(limit = MAX_ZIP_IMPORT_BYTES) {
  let remaining = limit;
  return (entry: JSZip.JSZipObject): Promise<string> => new Promise((resolve, reject) => {
    // JSZip exposes its browser stream helper at runtime but omits it from its types.
    const stream = (entry as JSZip.JSZipObject & {
      internalStream(type: 'uint8array'): ZipByteStream;
    }).internalStream('uint8array');
    const decoder = new TextDecoder();
    const chunks: string[] = [];
    stream.on('data', chunk => {
      remaining -= chunk.byteLength;
      if (remaining < 0) {
        stream.pause();
        chunks.length = 0;
        reject(new Error('Archive exceeds the expanded import size limit.'));
        return;
      }
      chunks.push(decoder.decode(chunk, { stream: true }));
    }).on('error', reject).on('end', () => {
      chunks.push(decoder.decode());
      resolve(chunks.join(''));
    }).resume();
  });
}

import type { Chapter } from '@/types';

/** Coalesces patches without dropping other fields or chapters, and orders writes. */
export class ChapterSaveQueue {
  private pending = new Map<string, Partial<Chapter>>();
  private timer: ReturnType<typeof setTimeout> | undefined;
  private inFlight: Promise<void> | undefined;

  constructor(
    private write: (id: string, updates: Partial<Chapter>) => Promise<void>,
    private onDirty: (dirty: boolean) => void,
    private onError: (cause: unknown) => void,
    private delay: number,
    private journal?: {
      stage: (id: string, updates: Partial<Chapter>) => void;
      commit: (id: string, updates: Partial<Chapter>) => void;
    },
  ) {}

  setDelay(delay: number) {
    this.delay = delay;
    if (this.pending.size) this.schedule();
  }

  enqueue(id: string, updates: Partial<Chapter>) {
    this.pending.set(id, { ...this.pending.get(id), ...updates });
    this.onDirty(true);
    try {
      this.journal?.stage(id, this.pending.get(id)!);
    } catch (cause) {
      this.onError(cause);
      // If the synchronous recovery store is full, try the primary store now.
      void this.flush().catch(() => {});
      return;
    }
    this.schedule();
  }

  discard(id: string) {
    this.pending.delete(id);
    this.onDirty(this.pending.size > 0 || !!this.inFlight);
  }

  private schedule() {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => { void this.flush().catch(() => {}); }, this.delay);
  }

  async flush(): Promise<void> {
    clearTimeout(this.timer);
    if (this.inFlight) {
      await this.inFlight;
      return this.flush();
    }
    if (!this.pending.size) return;

    const batch = this.pending;
    this.pending = new Map();
    this.inFlight = this.saveBatch(batch);
    try {
      await this.inFlight;
    } finally {
      this.inFlight = undefined;
      this.onDirty(this.pending.size > 0);
    }
    // An explicit flush also includes edits queued while a write was in progress.
    if (this.pending.size) await this.flush();
  }

  private async saveBatch(batch: Map<string, Partial<Chapter>>) {
    let failure: unknown;
    let failed = false;
    for (const [id, updates] of batch) {
      try {
        await this.write(id, updates);
        this.journal?.commit(id, updates);
      } catch (cause) {
        // Retain failed patches for retry; newer edits always take precedence.
        this.pending.set(id, { ...updates, ...this.pending.get(id) });
        failure = cause;
        failed = true;
      }
    }
    if (failed) {
      this.onError(failure);
      throw failure;
    }
  }
}

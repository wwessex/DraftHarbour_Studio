import { useEffect, useRef } from 'react';
import { createProjectBackup } from '@/lib/storage';

export function useAutomaticBackups(novelId: string, flush: () => Promise<void>, onError: (cause: unknown) => void) {
  const callbacks = useRef({ flush, onError });
  callbacks.current = { flush, onError };
  useEffect(() => {
    if (!novelId) return;
    let running = false;
    let cancelled = false;
    const backup = async () => {
      if (running || cancelled) return;
      running = true;
      try {
        await callbacks.current.flush();
        if (!cancelled) await createProjectBackup(novelId, true);
      } catch (cause) { if (!cancelled) callbacks.current.onError(cause); }
      finally { running = false; }
    };
    const initial = window.setTimeout(() => { void backup(); }, 60_000);
    const interval = window.setInterval(() => { void backup(); }, 5 * 60_000);
    return () => { cancelled = true; window.clearTimeout(initial); window.clearInterval(interval); };
  }, [novelId]);
}

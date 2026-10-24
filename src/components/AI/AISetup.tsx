import { useState } from 'react';
import { createNarratryxConfig } from '@/lib/ai/narratryx';
import { DESKTOP_LOCAL_MODEL, inspectDesktopLocalAI, stopDesktopLocalAI, manageDesktopLocalPackage } from '@/lib/ai/desktopLocalProvider';
import { saveAIConfig } from '@/lib/ai/providerManager';
import styles from './WritingWorkspace.module.css';

import { setAISetupMode } from '@/lib/ai/setupPreferences';

/** Explicit choices only: no download, remote fallback or endpoint probing on mount. */
export function AISetup({ onChanged, onConfigure }: { onChanged: () => void; onConfigure?: () => void }) {
  const [status, setStatus] = useState('Install a reviewed package through the desktop app. Online sign-in is still in development.');
  const [checking, setChecking] = useState(false);
  const chooseLocal = async () => {
    setChecking(true); setStatus('Checking the local model package…');
    try {
      const model = await inspectDesktopLocalAI();
      if (model !== DESKTOP_LOCAL_MODEL) throw new Error('The verified local model identity does not match.');
      const config = createNarratryxConfig('http://127.0.0.1');
      config.customLlm = { ...config.customLlm!, model, managedRuntime: true };
      saveAIConfig(config);
      setAISetupMode('local');
      setStatus(`Verified ${model}. Starts when you request a draft. No key entry is needed.`);
      onChanged();
    } catch (error) { setStatus(`Local AI unavailable: ${error instanceof Error ? error.message : String(error)} Your current connection is unchanged. No text was sent online.`); }
    finally { setChecking(false); }
  };
  const decideLater = async () => {
    setChecking(true);
    try {
      await stopDesktopLocalAI();
      setAISetupMode('later');
      setStatus('AI is off. Keep writing and return to AI setup at any time.');
      onChanged();
    } catch { setStatus('Unable to stop Local AI. Try again before changing mode.'); }
    finally { setChecking(false); }
  };
  const existingConnection = async () => {
    setChecking(true);
    try {
      await stopDesktopLocalAI();
      setAISetupMode('existing'); onChanged(); onConfigure?.();
    } catch { setStatus('Unable to stop Local AI. Try again before changing mode.'); }
    finally { setChecking(false); }
  };
  const managePackage = async (action: 'install' | 'restore') => {
    setChecking(true); setStatus('Checking the package. Review the native confirmation before any replacement.');
    try {
      const model = await manageDesktopLocalPackage(action);
      if (model === null) { setStatus('Cancelled. The installed package and connection are unchanged.'); return; }
      if (model !== DESKTOP_LOCAL_MODEL) throw new Error('Unexpected local model identity.');
      setStatus(`${action === 'install' ? 'Installed' : 'Restored'} ${model}. Choose On this computer to use it.`);
    } catch (error) { setStatus(`Package operation unavailable: ${error instanceof Error ? error.message : String(error)}`); }
    finally { setChecking(false); }
  };
  return <section className={styles.panel} aria-label="AI setup">
    <p className={styles.hint}>Choose how AI runs. Online requests send the requested passage and context to the selected service.</p>
    <div className={styles.bar}>
      <button className={styles.action} disabled={checking} onClick={() => void chooseLocal()}>On this computer</button>
      <button className={styles.action} disabled>Online AI — coming soon</button>
      <button className={styles.action} disabled={checking} onClick={() => void decideLater()}>Decide later</button>
      <button className={styles.action} disabled={checking} onClick={() => void managePackage('install')}>Install local package…</button>
      <button className={styles.action} disabled={checking} onClick={() => void managePackage('restore')}>Restore previous package…</button>
      {onConfigure && <button className={styles.action} disabled={checking} onClick={() => void existingConnection()}>Use an existing connection…</button>}
    </div>
    <p className={styles.hint} role="status">{status}</p>
    <p className={styles.hint}>Drafting needs no account or model. The managed local runtime needs no training or user-entered key. Browser and iOS capabilities differ from desktop.</p>
  </section>;
}

/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { AppState } from '@/types';
import { createInitialAppState } from '@/context/state/appReducer';
import { useProjectFileActions } from './useProjectFileActions';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const mocks = vi.hoisted(() => ({ exportBackup: vi.fn(), exportDhproj: vi.fn(), importBackup: vi.fn(), importDhproj: vi.fn(), downloadFile: vi.fn() }));
vi.mock('@/lib/storage', () => ({ ...mocks }));
vi.mock('@/lib/utils', async () => ({ ...await vi.importActual('@/lib/utils'), downloadFile: mocks.downloadFile }));

let root: ReturnType<typeof createRoot>;
let actions: ReturnType<typeof useProjectFileActions>;
const flushPendingSaves = vi.fn<() => Promise<void>>();
const showToast = vi.fn();
const loadNovelById = vi.fn(async () => {});
beforeEach(async () => {
  vi.clearAllMocks();
  mocks.importBackup.mockResolvedValue({ id: 'restored' });
  mocks.importDhproj.mockResolvedValue({ id: 'restored' });
  mocks.exportBackup.mockResolvedValue({ sections: [{ content: 'Latest draft' }] });
  mocks.exportDhproj.mockResolvedValue(new Blob(['Latest draft']));
  flushPendingSaves.mockResolvedValue();
  const state: AppState = { ...createInitialAppState(), novelId: 'project', novelTitle: 'My Novel' };
  function Probe() {
    actions = useProjectFileActions({ state, loadNovel: vi.fn(), loadNovelById, flushPendingSaves, showToast });
    return null;
  }
  root = createRoot(document.createElement('div'));
  await act(async () => root.render(<Probe />));
});
afterEach(async () => {
  await act(async () => root.unmount());
  vi.clearAllTimers();
  vi.useRealTimers();
});

it.each(['backup', 'project'] as const)('flushes edits before importing a %s and resets the file input', async format => {
  vi.useFakeTimers();
  const data = { sections: [{ content: 'Restored draft' }] };
  const file = new File([JSON.stringify(data)], 'restore.json');
  // jsdom File does not implement text() in every supported version.
  Object.defineProperty(file, 'text', { value: async () => JSON.stringify(data) });
  const target = { files: [file], value: 'restore.json' };
  const event = { target } as unknown as React.ChangeEvent<HTMLInputElement>;
  await (format === 'backup' ? actions.handleImportBackup(event) : actions.handleOpenProjectFile(event));
  expect(flushPendingSaves).toHaveBeenCalledOnce();
  if (format === 'backup') expect(mocks.importBackup).toHaveBeenCalledWith(data);
  else expect(mocks.importDhproj).toHaveBeenCalledWith(file);
  expect(target.value).toBe('');
  expect(loadNovelById).toHaveBeenCalledWith('restored');
  expect(showToast).toHaveBeenCalledWith(expect.stringContaining('successfully'), 'success');
});

it.each(['backup', 'project'] as const)('keeps the current manuscript open if saving fails before %s import', async format => {
  vi.useFakeTimers();
  const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
  flushPendingSaves.mockRejectedValueOnce(new Error('Storage full'));
  const file = new File(['{}'], 'restore.json');
  Object.defineProperty(file, 'text', { value: async () => '{}' });
  const target = { files: [file], value: 'restore.json' };
  const event = { target } as unknown as React.ChangeEvent<HTMLInputElement>;
  try {
    await (format === 'backup' ? actions.handleImportBackup(event) : actions.handleOpenProjectFile(event));
    expect(mocks.importBackup).not.toHaveBeenCalled();
    expect(mocks.importDhproj).not.toHaveBeenCalled();
    expect(target.value).toBe('');
    expect(showToast).toHaveBeenCalledWith(expect.any(String), 'error');
    expect(vi.getTimerCount()).toBe(0);
  } finally { consoleError.mockRestore(); }
});

it.each(['backup', 'project'] as const)('waits for pending manuscript saves before exporting a %s', async format => {
  let finish!: () => void;
  flushPendingSaves.mockReturnValueOnce(new Promise<void>(resolve => { finish = resolve; }));
  const operation = format === 'backup' ? actions.handleExportBackup() : actions.handleSaveProjectFile();
  expect(flushPendingSaves).toHaveBeenCalledOnce();
  expect(mocks.exportBackup).not.toHaveBeenCalled();
  expect(mocks.exportDhproj).not.toHaveBeenCalled();
  finish();
  await operation;
  expect(mocks.downloadFile).toHaveBeenCalledOnce();
  if (format === 'backup') expect(mocks.downloadFile.mock.calls[0][0]).toContain('Latest draft');
});

it.each(['backup', 'project'] as const)('does not download a stale %s when saving fails', async format => {
  const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
  flushPendingSaves.mockRejectedValueOnce(new Error('Storage full'));
  try {
    await (format === 'backup' ? actions.handleExportBackup() : actions.handleSaveProjectFile());
    expect(mocks.downloadFile).not.toHaveBeenCalled();
    expect(mocks.exportBackup).not.toHaveBeenCalled();
    expect(mocks.exportDhproj).not.toHaveBeenCalled();
    expect(showToast).toHaveBeenCalledWith(expect.any(String), 'error');
  } finally { consoleError.mockRestore(); }
});

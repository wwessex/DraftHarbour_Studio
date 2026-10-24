export const AI_SETUP_MODE_KEY = 'draftharbour_ai_setup_mode_v1';
export const AI_SETUP_CHANGED = 'draftharbour-ai-setup-changed';
export type AISetupMode = 'local' | 'existing' | 'later';

export function getAISetupMode(): AISetupMode {
  const mode = localStorage.getItem(AI_SETUP_MODE_KEY);
  return mode === 'local' || mode === 'later' ? mode : 'existing';
}
export function setAISetupMode(mode: AISetupMode): void {
  const changed = getAISetupMode() !== mode;
  localStorage.setItem(AI_SETUP_MODE_KEY, mode);
  if (changed) window.dispatchEvent(new Event(AI_SETUP_CHANGED));
}

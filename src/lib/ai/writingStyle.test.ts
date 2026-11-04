import { describe, expect, it } from 'vitest';
import { NATURAL_WRITING_STYLE, withNaturalWritingStyle } from './writingStyle';
import type { AIRequest } from './types';

describe('natural writing defaults', () => {
  it.each(['continue', 'rewrite', 'copyedit', 'grammar', 'translate', 'custom', 'chat', 'analysis'])('retains the %s task and transport controls', action => {
    const controller = new AbortController();
    const onStreamChunk = () => {};
    const request: AIRequest = { action, prompt: 'Return only JSON with the exact source anchor "🐦".', context: 'Read-only canon. TARGET PASSAGE: An old bell.', projectType: 'screenplay', sectionTitle: 'Quay', signal: controller.signal, onStreamChunk };
    const styled = withNaturalWritingStyle(request);
    expect(styled).toEqual({ ...request, prompt: NATURAL_WRITING_STYLE + '\n\n' + request.prompt });
    expect(request.prompt).not.toContain('Writing style:');
    expect(withNaturalWritingStyle(styled)).toBe(styled);
    expect(styled.signal).toBe(controller.signal);
    expect(styled.onStreamChunk).toBe(onStreamChunk);
  });
});

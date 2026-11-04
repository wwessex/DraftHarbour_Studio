import type { AIRequest } from './types';

/** Default prose guidance, subordinate to the author's task and output contract. */
export const NATURAL_WRITING_STYLE = "Writing style: Follow the author's task, requested voice, language, scope and output format first. For new prose and rewrites, match the supplied author's voice, viewpoint, tense and register. Prefer concrete details, precise verbs, natural dialogue and varied sentence lengths. Avoid stock phrases, repetitive rhythms, inflated language, generic transitions and unnecessary summaries or explanations. For chat, feedback and suggestions, be direct, specific and conversational. Do not add deliberate mistakes, invented facts or claims of human authorship. For copyediting, grammar, translation and structured output, preserve meaning, edit boundaries, exact anchors and required schemas; apply style only where the task permits. Return only the requested output.";

export function withNaturalWritingStyle(request: AIRequest): AIRequest {
  if (request.prompt.startsWith(NATURAL_WRITING_STYLE + '\n\n')) return request;
  return { ...request, prompt: NATURAL_WRITING_STYLE + '\n\n' + request.prompt };
}

/**
 * agent.ts — TeamFlow AI chat API.
 *
 * askAgent() → POST /agent/ask
 * Returns only the answer string; sources are intentionally discarded.
 */

import { apiClient } from './client';

export async function askAgent(
  question: string,
  threadId: string,
): Promise<string> {
  const res = await apiClient('/agent/ask', {
    method: 'POST',
    body: JSON.stringify({ question, thread_id: threadId }),
  });

  if (!res.ok) {
    throw new Error(`Agent request failed: ${res.status}`);
  }

  const data = await res.json();
  // data.sources is ignored per design decision.
  return data.answer as string;
}

const key = (novelId: string) => `draftharbour_saved_searches_v1_${novelId}`;
export function loadSavedSearches(novelId: string): string[] {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(key(novelId)) || '[]');
    return Array.isArray(data) ? data.filter((item): item is string => typeof item === 'string' && !!item.trim()).slice(0, 10) : [];
  } catch { return []; }
}
export function saveSearches(novelId: string, queries: string[]): void {
  localStorage.setItem(key(novelId), JSON.stringify([...new Set(queries.map(query => query.trim()).filter(Boolean))].slice(0, 10)));
}

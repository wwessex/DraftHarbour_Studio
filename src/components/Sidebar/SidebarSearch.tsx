import { useState, useEffect, useRef, useCallback, useId } from 'react';
import { useApp } from '@/context/AppContext';
import { searchManuscript } from '@/lib/desktopWritingEngine';
import type { ChapterSearchResult } from '@/lib/search';
import { loadSavedSearches, saveSearches } from '@/lib/savedSearches';
import styles from './SidebarSearch.module.css';

const DEBOUNCE_MS = 200;

export function SidebarSearch() {
  const { state, setActiveChapter } = useApp();
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [results, setResults] = useState<ChapterSearchResult[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const listId = useId();
  const [activeResult, setActiveResult] = useState(0);
  const [saved, setSaved] = useState<string[]>([]);
  const [searchError, setSearchError] = useState('');
  useEffect(() => { setSaved(loadSavedSearches(state.novelId)); }, [state.novelId]);

  useEffect(() => {
    const handle = window.setTimeout(() => setDebouncedQuery(query), DEBOUNCE_MS);
    return () => window.clearTimeout(handle);
  }, [query]);

  useEffect(() => {
    let cancelled = false;
    setActiveResult(0);
    if (!debouncedQuery.trim()) {
      setResults([]);
      return;
    }

    void searchManuscript(state.chapters, debouncedQuery, 20)
      .then(matches => {
        if (!cancelled) setResults(matches);
      })
      .catch(error => {
        console.error('Whole-manuscript search failed:', error);
        if (!cancelled) setResults([]);
      });

    return () => {
      cancelled = true;
    };
  }, [state.chapters, debouncedQuery]);

  const handleSelect = useCallback((chapterId: string) => {
    setActiveChapter(chapterId);
    setQuery('');
    setExpanded(false);
  }, [setActiveChapter]);

  const handleToggle = useCallback(() => {
    setExpanded(prev => {
      if (!prev) {
        setTimeout(() => inputRef.current?.focus(), 60);
      }
      return !prev;
    });
    setQuery('');
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && results.length) {
      e.preventDefault();
      setActiveResult(index => (index + (e.key === 'ArrowDown' ? 1 : -1) + results.length) % results.length);
    }
    if (e.key === 'Enter' && results[activeResult] && query === debouncedQuery) {
      e.preventDefault();
      handleSelect(results[activeResult].chapterId);
    }
    if (e.key === 'Escape') {
      setQuery('');
      setExpanded(false);
    }
  }, [results, activeResult, query, debouncedQuery, handleSelect]);

  const updateSaved = (queries: string[]) => {
    try { saveSearches(state.novelId, queries); setSaved(loadSavedSearches(state.novelId)); setSearchError(''); }
    catch { setSearchError('Could not save this search. Manuscript saving is unaffected.'); }
  };

  return (
    <div className={styles.searchContainer}>
      <button
        type="button"
        className={`${styles.searchToggle} ${expanded ? styles['searchToggle--active'] : ''}`}
        onClick={handleToggle}
        aria-expanded={expanded}
        aria-label="Search all chapters"
      >
        <span className="material-symbols-rounded">search</span>
        <span className={styles.searchToggleLabel}>Search</span>
      </button>
      {expanded && (
        <div className={styles.searchPanel}>
          <input
            ref={inputRef}
            className={styles.searchInput}
            type="text"
            role="combobox"
            aria-label="Search manuscript"
            aria-expanded={!!debouncedQuery.trim()}
            aria-controls={listId}
            aria-activedescendant={results[activeResult] ? `${listId}-${activeResult}` : undefined}
            aria-autocomplete="list"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search all chapters..."
            autoComplete="off"
            spellCheck={false}
          />
          <button type="button" disabled={!query.trim()} onClick={() => updateSaved([query, ...saved])}>Save search</button>
          {saved.map(term => <div key={term}>
            <button type="button" onClick={() => setQuery(term)}>{term}</button>
            <button type="button" aria-label={`Remove saved search ${term}`} onClick={() => updateSaved(saved.filter(item => item !== term))}>×</button>
          </div>)}
          {searchError && <p role="status">{searchError}</p>}
          {debouncedQuery.trim() && (
            <div className={styles.searchResults} role="listbox" id={listId} aria-label="Manuscript search results">
              {results.length === 0 ? (
                <div className={styles.searchEmpty}>No matches found</div>
              ) : (
                <>
                  <div className={styles.searchCount}>{results.length} match{results.length !== 1 ? 'es' : ''}</div>
                  {results.map((result, idx) => (
                    <button
                      key={`${result.chapterId}-${result.match.start}-${idx}`}
                      type="button"
                      className={styles.searchResult}
                      onClick={() => handleSelect(result.chapterId)}
                      role="option"
                      id={`${listId}-${idx}`}
                      aria-selected={idx === activeResult}
                      onMouseEnter={() => setActiveResult(idx)}
                    >
                      <span className={styles.searchResultTitle}>{result.chapterTitle}</span>
                      <span className={styles.searchResultSnippet}>{result.snippet}</span>
                    </button>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

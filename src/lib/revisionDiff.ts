/** Align insertions/deletions so one changed paragraph does not highlight the rest. */
export function alignRevisionLines(oldText: string, newText: string) {
  const old = oldText.split('\n');
  const next = newText.split('\n');
  const oldLines: Array<string | null> = [];
  const newLines: Array<string | null> = [];
  let prefix = 0;
  while (prefix < old.length && prefix < next.length && old[prefix] === next[prefix]) {
    oldLines.push(old[prefix]); newLines.push(next[prefix]); prefix++;
  }
  let suffix = 0;
  while (suffix < old.length - prefix && suffix < next.length - prefix && old[old.length - 1 - suffix] === next[next.length - 1 - suffix]) suffix++;
  const a = old.slice(prefix, old.length - suffix);
  const b = next.slice(prefix, next.length - suffix);
  if (a.length * b.length > 1_000_000) {
    for (const line of a) { oldLines.push(line); newLines.push(null); }
    for (const line of b) { oldLines.push(null); newLines.push(line); }
  } else {
    const lengths = Array.from({ length: a.length + 1 }, () => new Uint32Array(b.length + 1));
    for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) {
      lengths[i][j] = a[i] === b[j] ? lengths[i + 1][j + 1] + 1 : Math.max(lengths[i + 1][j], lengths[i][j + 1]);
    }
    let i = 0, j = 0;
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) { oldLines.push(a[i++]); newLines.push(b[j++]); }
      else if (j < b.length && (i === a.length || lengths[i][j + 1] >= lengths[i + 1][j])) { oldLines.push(null); newLines.push(b[j++]); }
      else { oldLines.push(a[i++]); newLines.push(null); }
    }
  }
  for (let i = suffix; i > 0; i--) { oldLines.push(old[old.length - i]); newLines.push(next[next.length - i]); }
  return { oldLines, newLines };
}

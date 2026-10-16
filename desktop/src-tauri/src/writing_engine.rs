use serde::{Deserialize, Serialize};
use unicode_normalization::{char::is_combining_mark, UnicodeNormalization};

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ManuscriptDocument {
    pub id: String,
    pub title: String,
    pub plain_text: String,
}

#[derive(Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SearchMatchRange {
    pub start: usize,
    pub end: usize,
}

#[derive(Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ManuscriptSearchResult {
    pub chapter_id: String,
    pub chapter_title: String,
    pub snippet: String,
    pub match_range: SearchMatchRange,
    pub score: u32,
}

#[derive(Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DocumentStatistics {
    pub id: String,
    pub words: usize,
    pub sentences: usize,
    pub paragraphs: usize,
    pub characters: usize,
}

#[derive(Debug, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ManuscriptStatistics {
    pub documents: Vec<DocumentStatistics>,
    pub total_words: usize,
    pub total_sentences: usize,
    pub total_paragraphs: usize,
    pub total_characters: usize,
}

fn normalize(text: &str) -> String {
    text.nfkd()
        .filter(|character| !is_combining_mark(*character))
        .flat_map(char::to_lowercase)
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

fn snippet(content: &str, start: usize, end: usize, radius: usize) -> String {
    let characters = content.chars().collect::<Vec<_>>();
    let snippet_start = start.saturating_sub(radius);
    let snippet_end = characters.len().min(end.saturating_add(radius));
    let body = characters[snippet_start..snippet_end]
        .iter()
        .collect::<String>()
        .trim()
        .to_string();
    format!(
        "{}{}{}",
        if snippet_start > 0 { "…" } else { "" },
        body,
        if snippet_end < characters.len() {
            "…"
        } else {
            ""
        }
    )
}

pub fn search(
    documents: &[ManuscriptDocument],
    raw_query: &str,
    max_results: usize,
) -> Vec<ManuscriptSearchResult> {
    let query = normalize(raw_query);
    if query.is_empty() || max_results == 0 {
        return Vec::new();
    }

    let mut results = Vec::new();
    for document in documents {
        let normalized_text = normalize(&document.plain_text);
        let title_boost = if normalize(&document.title).contains(&query) {
            12
        } else {
            0
        };
        let mut from_index = 0;

        while results.len() < max_results {
            let Some(relative_start) = normalized_text[from_index..].find(&query) else {
                break;
            };
            let byte_start = from_index + relative_start;
            let byte_end = byte_start + query.len();
            let start = normalized_text[..byte_start].chars().count();
            let end = start + query.chars().count();
            results.push(ManuscriptSearchResult {
                chapter_id: document.id.clone(),
                chapter_title: document.title.clone(),
                snippet: snippet(&document.plain_text, start, end, 80),
                match_range: SearchMatchRange { start, end },
                score: 40 + title_boost,
            });
            from_index = byte_end;
        }

        if results.len() >= max_results {
            break;
        }
    }

    results
}

fn statistics_for(document: &ManuscriptDocument) -> DocumentStatistics {
    let text = document.plain_text.trim();
    let words = text.split_whitespace().count();
    let sentences = text
        .chars()
        .fold((0usize, false), |(count, in_mark), character| {
            let is_mark = matches!(character, '.' | '!' | '?');
            (count + usize::from(is_mark && !in_mark), is_mark)
        })
        .0;
    let paragraphs = text
        .split('\n')
        .filter(|paragraph| !paragraph.trim().is_empty())
        .count();
    let characters = text
        .chars()
        .filter(|character| !character.is_whitespace())
        .count();

    DocumentStatistics {
        id: document.id.clone(),
        words,
        sentences,
        paragraphs,
        characters,
    }
}

pub fn statistics(documents: &[ManuscriptDocument]) -> ManuscriptStatistics {
    let documents = documents.iter().map(statistics_for).collect::<Vec<_>>();
    ManuscriptStatistics {
        total_words: documents.iter().map(|document| document.words).sum(),
        total_sentences: documents.iter().map(|document| document.sentences).sum(),
        total_paragraphs: documents.iter().map(|document| document.paragraphs).sum(),
        total_characters: documents.iter().map(|document| document.characters).sum(),
        documents,
    }
}

pub fn validate_backup_json(contents: &str) -> Result<(), String> {
    let value: serde_json::Value = serde_json::from_str(contents)
        .map_err(|error| format!("Backup is not valid JSON: {error}"))?;
    let object = value
        .as_object()
        .ok_or_else(|| "Backup root must be an object.".to_string())?;
    let version = object
        .get("version")
        .and_then(serde_json::Value::as_u64)
        .ok_or_else(|| "Backup is missing a numeric version.".to_string())?;
    if !(1..=3).contains(&version) {
        return Err(format!("Unsupported backup version: {version}."));
    }
    let has_expected_data = if version == 3 {
        object.contains_key("project") && object.contains_key("sections")
    } else {
        object.contains_key("novel") && object.contains_key("chapters")
    };
    if !has_expected_data {
        return Err("Backup is missing its project and section data.".to_string());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn documents() -> Vec<ManuscriptDocument> {
        vec![ManuscriptDocument {
            id: "chapter-1".into(),
            title: "The Café".into(),
            plain_text: "Rain fell. The café was quiet!\n\nThen the door opened?".into(),
        }]
    }

    #[test]
    fn search_is_case_and_diacritic_insensitive() {
        let results = search(&documents(), "CAFE", 20);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].chapter_id, "chapter-1");
        assert_eq!(results[0].score, 52);
        assert!(results[0].snippet.contains("café"));
    }

    #[test]
    fn search_handles_multibyte_text_before_a_match() {
        let documents = vec![ManuscriptDocument {
            id: "chapter-1".into(),
            title: "Multilingual".into(),
            plain_text: "東京 café".into(),
        }];
        let results = search(&documents, "cafe", 20);
        assert_eq!(results.len(), 1);
        assert_eq!(
            results[0].match_range,
            SearchMatchRange { start: 3, end: 7 }
        );
        assert!(results[0].snippet.contains("café"));
    }

    #[test]
    fn statistics_cover_the_complete_manuscript() {
        let result = statistics(&documents());
        assert_eq!(result.total_words, 10);
        assert_eq!(result.total_sentences, 3);
        assert_eq!(result.total_paragraphs, 2);
        assert_eq!(result.documents.len(), 1);
    }

    #[test]
    fn backup_validation_accepts_current_shape_and_rejects_unknown_versions() {
        assert!(validate_backup_json(r#"{"version":3,"project":{},"sections":[]}"#).is_ok());
        assert!(validate_backup_json(r#"{"version":9,"project":{},"sections":[]}"#).is_err());
    }
}

"""Source overlap and narrow repair diagnostics; no model selection or training."""


def require_distinct_source_spans(records: list[dict], ledger: dict) -> None:
    spans=[]
    for row in records:
        for s in row['source_spans']:
            identity=ledger[s['rights_record_id']]['source']['sha256']
            for other_id,other_hash,start,end in spans:
                if other_id != row['id'] and identity == other_hash and max(start,s['start']) < min(end,s['end']):
                    raise ValueError(f'overlapping source variants: {other_id}, {row["id"]}')
            spans.append((row['id'],identity,s['start'],s['end']))


def repair_diagnostics(output: str, binding: dict) -> dict:
    """Strict characters; lexical anchor presence alone is not a correct repair."""
    source=binding['source_answer'];start=binding['start'];end=binding['source_end']
    prefix=source[:start];suffix=source[end:]
    outside=output.startswith(prefix) and output.endswith(suffix) and len(output)>=len(prefix)+len(suffix)
    middle=output[len(prefix):len(output)-len(suffix) if suffix else None] if outside else None
    return dict(exact_full_answer=output==source,outside_correction_preserved=outside,
                correction_at_expected_slot=middle==binding['original'] if outside else None,
                correct_anchor_present_once=output.count(binding['original'])==1 and output.count(binding['wrong'])==source.count(binding['wrong']))

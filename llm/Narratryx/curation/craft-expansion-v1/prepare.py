"""Record scoped AI evidence review and fail-closed pilot preflight; no training."""
from pathlib import Path
import hashlib, json, re, sys, os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import validate_schema, validate_dataset, clear_source, load_ledger, check_leakage
P=ROOT/'artifacts/craft-expansion-v1'
LEDGER=ROOT/'rights/craft-expansion-v1.scoped.jsonl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    with p.open('x') as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')
def readrows(p):return [json.loads(l) for l in p.read_text().splitlines()]

def main():
    acquisition=json.loads((ROOT/'rights/raw/craft-expansion-2026-10-20/acquisition.json').read_text())
    scope=json.loads((P/'scope.json').read_text())
    sources=[
        ('wharton-writing','Edith Wharton','1862–1937',1937,1925,'The Writing of Fiction','Charles Scribner’s Sons, New York/London','Title matter identifies 1925 printing; copyrights 1924/1925. Physical copy not independently collated.', 'training'),
        ('hamilton-manual','Clayton Meeker Hamilton','1881–1946',1946,1918,'A Manual of the Art of Fiction','Doubleday, Page & Company, Garden City–New York','Title matter identifies 1919 printing of copyright-1918 revised work, not a 1918 printing. Introduction by Brander Matthews excluded.', 'training'),
        ('mansfield-garden','Katherine Mansfield','1888–1923',1923,1922,'The Garden Party and Other Stories','Original collection: Constable & Company, London; exact PG physical copy unidentified','Pinned PG1429 digital artifact. Original 1922 authored stories only; no claim this file transcribes a particular 1922 Constable or 1923 Knopf printing.', 'evaluation'),
        ('chesnutt-conjure','Charles W. Chesnutt','1858–1932',1932,1899,'The Conjure Woman','Original collection: Houghton, Mifflin & Co.; exact PG physical copy unidentified','Pinned PG11666 digital artifact. Header identifies original publication 1899, not exact physical printing. Only selected original-collection prose; appended other works excluded.', 'evaluation'),
    ]
    ledger=[]
    for ident,author,life,death,year,title,publisher,edition,use in sources:
        a=next(x for x in acquisition if x['id']==ident)
        catalogue=f'https://www.gutenberg.org/ebooks/{a["pg_id"]}'
        spans=[s for s in scope if s['source_id']==ident]
        assert spans and {s['use'] for s in spans}=={use}
        r=dict(schema_version='1.0', id=ident,work_id=ident,title=title,source_kind='public_domain_candidate',
               author_ids=[author.lower().replace(' ','-').replace('.','')],
               contributors=[dict(name=author,role='author of selected original prose only',life_dates=life)],
               publication=dict(original_year=year,edition=edition,publisher=publisher,evidence=[catalogue,a['url']]),
               source=dict(url=a['url'],retrieved_on=a['retrieved_on'],revision='sha256:'+a['sha256'],raw_path=a['raw_path'],sha256=a['sha256'],
                 included_material=f'Only the {len(spans)} exact LF-normalized Unicode spans for {ident} in artifacts/craft-expansion-v1/scope.json, SHA256 {sha(P/"scope.json")}; use {use}. No whole-book clearance.',
                 excluded_material='Provider wrapper/license/branding, modern catalogue summaries, title matter, epigraphs, dedications, introductions by others, editorial/transcriber notes, illustrations, footnotes, quoted third-party extracts, reading lists and appendices. No physical page layout. Hamilton earlier edition is comparison research only, not training.',
                 terms_evidence=[catalogue,'https://www.gutenberg.org/MIRRORS.ALL','https://www.gutenberg.org/policy/terms_of_use.html','https://www.gutenberg.org/policy/license.html','https://www.gutenberg.org/policy/permission.html'],
                 terms_decision='AI source evidence review supports local private use of selected unbranded, expired original prose in GB/US without a new rights-holder grant. Full original files/notices retained. No separately protected modern additions, provider endorsement, branded redistribution, cloud upload or publication authorized by this record. This is not human approval or legal certification.',
                 notices='Original UTF-8 file and complete provider notices retained byte-for-byte in rights/raw. Item-specific US-PD status checked. Exact digital artifact pinned; physical-printing uncertainty is stated, not resolved by invention.'),
               clearances=[dict(jurisdiction='GB',basis=f'Original literary author died {death}; ordinary life+70 term expired by end {death+70}. Only authored original prose is included; later independent contributions and layout excluded.',uses=[use],evidence=['https://www.gov.uk/copyright/how-long-copyright-lasts',catalogue]),
                           dict(jurisdiction='US',basis=f'Item-specific provider determination: public domain in USA. Underlying prose published {year}, before 1931, with applicable maximum historical US term elapsed in 2026. Modern separately protected material excluded.',uses=[use],evidence=[catalogue,'https://www.copyright.gov/circs/circ15a.pdf'])],
               unresolved_issues=[],review=dict(status='approved',reviewer='Codex AI: scoped source evidence assessment',reviewed_on='2026-10-20',notes='AI assessment under user instruction to proceed with sources needing no permission. No human ballot or lawyer approval recorded. Edition uncertainty disclosed; clearance concerns specified original prose, not unverifiable later matter. Evidence/dossier and scope hashes retained.'))
        validate_schema(r,'rights-record');ledger.append(r)
    ledger_text=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ledger)
    if LEDGER.exists():
        assert LEDGER.read_text()==ledger_text, 'Refuse replacing a changed rights decision'
    else:
        with LEDGER.open('x') as f:f.write(ledger_text)
    records=validate_dataset(P/'train.records.jsonl',LEDGER,['GB','US'])
    cases=readrows(P/'test.cases.jsonl');contexts=readrows(P/'test.contexts.jsonl')
    index=load_ledger(LEDGER)
    assert len(cases)==16 and len(contexts)==4 and len(records)==20
    for c in contexts:
        raw=clear_source(index[c['source_id']],LEDGER,['GB','US'],'evaluation')
        assert raw[c['start']:c['end']]==c['raw_text']
        assert ' '.join(c['raw_text'].split())==c['text']
    check_leakage(records,[dict(id=c['id'],split_group=c['source_id'],context=c['text']) for c in contexts])
    assert not ({r['rights_record_ids'][0] for r in records}&{c['source_id'] for c in contexts})
    from transformers import AutoTokenizer
    model=Path('/Users/williamwessex/.cache/huggingface/hub/models--mlx-community--Qwen3.5-4B-MLX-8bit/snapshots/5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d')
    tok=AutoTokenizer.from_pretrained(str(model),local_files_only=True,trust_remote_code=False)
    tokenrows=[];total=0
    for r in records:
        answer=r['messages'][1]['content']
        raw=r['source_spans'][0]['text']
        assert re.sub(r'^=[^=]+=[—-]*\s*','',' '.join(raw.split()))==answer
        prefix=tok.apply_chat_template(r['messages'][:1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        pids=tok.encode(prefix,add_special_tokens=False);aids=tok.encode(answer,add_special_tokens=False)
        assert tok.decode(aids)==answer
        ids=pids+aids+[tok.eos_token_id];labels=[-100]*len(pids)+aids+[tok.eos_token_id]
        assert len(ids)<=1024
        tokenrows.append(dict(input_ids=ids,attention_mask=[1]*len(ids),labels=labels));total+=len(aids)+1
    from unsloth_zoo.mlx.utils import _tokenize_mlx_pretokenized_row
    for r in tokenrows:
        result=_tokenize_mlx_pretokenized_row(r,assistant_only_loss=True)
        assert result[1]==r['labels']
    with (P/'train.tokens.jsonl').open('x') as f:
        for r in tokenrows:f.write(json.dumps(r)+'\n')
    save(P/'validation.json',dict(passed=True,records=20,contexts=4,cases=16,ledger_records=4,source_hashes_verified=True,
        exact_source_spans_verified=True,answer_transform_roundtrips=20,tokenizer_roundtrips=20,explicit_label_roundtrips=20,
        supervised_tokens=total,max_sequence_tokens=max(len(r['input_ids']) for r in tokenrows),
        author_work_separation=True,lexical_leakage_screen_passed=True,editing_minimum_words=0,
        human_approval_recorded=False,legal_certification=False,
        files={str(p.relative_to(ROOT)):sha(p) for p in [LEDGER,P/'scope.json',P/'train.records.jsonl',P/'train.tokens.jsonl',P/'test.contexts.jsonl',P/'test.cases.jsonl']},
        base_weights_sha256=sha(model/'model.safetensors')))
    print('Scoped rights, spans, answers, splits and explicit training labels validated. Supervised tokens:',total)

if __name__=='__main__':main()

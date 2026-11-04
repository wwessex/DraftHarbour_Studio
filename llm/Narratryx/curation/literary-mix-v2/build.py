"""Broader source-only instruction curriculum; no generated literary answers."""
from pathlib import Path
import copy,hashlib,json,math,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import digest,validate_dataset
P=ROOT/'artifacts/literary-mix-v2'
LEDGER=ROOT/'rights/literary-mix-v2.scoped.jsonl'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return [json.loads(line) for line in p.read_text().splitlines()]
def rows(p,values):
    with p.open('x') as f:
        for value in values:f.write(json.dumps(value,ensure_ascii=False)+'\n')
def cap(text):return 10*math.ceil(len(text.split())/10)
def write_prompt(text,genre):
    words=text.split();opening=' '.join(words[:8]);closing=' '.join(words[-8:])
    return f'Write one coherent {genre} prose paragraph in at most {cap(text)} words. Include the exact opening and closing below as part of the paragraph. Preserve the narrator, tense and situation implied by these anchors. Return only the complete paragraph, without a heading or explanation.\n\nOPENING:\n{opening}\n\nCLOSING:\n{closing}'

def new_record(ident,task,prompt,target,source,span,work):
    messages=[dict(role='user',content=prompt),dict(role='assistant',content=target)]
    return dict(schema_version='1.0',id=ident,dataset_version='literary-mix-v2',task=task,split='train',split_group=source,origin='derived',messages=messages,source_work_ids=[work],rights_record_ids=[source],source_spans=[span],teacher=None,review=dict(status='approved',reviewer='Codex AI: exact source derivation and task alignment audit',reviewed_on='2026-10-25',notes='AI audit, not human literary approval. Answer is unchanged source prose/subspan. Anchored Write is conditional infilling, not an unconstrained author-written response to a new brief. Reference repair is a constructed exercise, not a genuine author revision.'),rubric=['coherence','usefulness'],content_hash=digest(messages))

def main():
    source_audit=json.loads((P/'source-audit.json').read_text())
    assert source_audit['passed'] and sha(P/'new-source-spans.json')==source_audit['scope_sha256']
    prior=json.loads((ROOT/'artifacts/literary-mix-training-v1/protocol.frozen.json').read_text())
    assert sha(ROOT/'artifacts/literary-mix-v1/records.jsonl')==prior['input_hashes']['artifacts/literary-mix-v1/records.jsonl']
    old=validate_dataset(ROOT/'artifacts/literary-mix-v1/records.jsonl',ROOT/'rights/literary-mix-v1.scoped.jsonl',['GB','US'])
    records=[];trace=[]
    for original in old:
        record=copy.deepcopy(original);record.pop('_author_ids',None)
        record['id']='v2-'+record['id'];record['dataset_version']='literary-mix-v2'
        if record['split']=='train' and record['task'] in ['fiction','dialogue','analysis']:
            # Only change the instruction. Do not shorten, rewrite or generate answers.
            target=record['messages'][-1]['content']
            record['messages'][0]['content']='Use at most '+str(cap(target))+' words.\n'+record['messages'][0]['content']
            record['review']=dict(status='approved',reviewer='Codex AI: source-target length constraint audit',reviewed_on='2026-10-25',notes='Prior exact source answer unchanged; instruction cap is greater than or equal to its whitespace-counted word count. No minimum imposed on editing. AI assessment, not human quality review.')
        record['content_hash']=digest(record['messages']);records.append(record)
        trace.append(dict(id=record['id'],prior_record_id=original['id'],prior_file_sha256=sha(ROOT/'artifacts/literary-mix-v1/records.jsonl'),answer_unchanged=True))
    # One anchored Write target per already scoped Opie paragraph, separate from continuations.
    for excerpt in read(ROOT/'artifacts/source-tasks-v1/excerpts.jsonl'):
        if excerpt['sid']!='opie-father-daughter-pg49621':continue
        target=excerpt['text'];span=excerpt['span']
        assert target==' '.join(span['text'].split())
        ident=f'v2-directed-opie-{len(trace):04d}'
        records.append(new_record(ident,'fiction',write_prompt(target,'period social-fiction'),target,excerpt['sid'],span,excerpt['work']))
        trace.append(dict(id=ident,source_span=span,target_start=0,target_end=len(target),target_sha256=hashlib.sha256(target.encode()).hexdigest(),kind='anchored-Write source reconstruction'))
    for i,excerpt in enumerate(json.loads((P/'new-source-spans.json').read_text())):
        target=excerpt['text'];source=excerpt['source_id'];work='the-time-machine' if source.startswith('wells') else 'adventures-of-sherlock-holmes'
        span=dict(rights_record_id=source,start=excerpt['start'],end=excerpt['end'],text=excerpt['raw_text'])
        words=list(re.finditer(r'\S+',target));cut=words[len(words)//2].start()
        tail=target[cut:]
        corrupted=target
        negation=re.search(r'\bnot\s+',target)
        if negation:corrupted=target[:negation.start()]+target[negation.end():];repair_kind='restore omitted negation from explicit reference'
        elif '’' in target:corrupted=target.replace('’',"'",1);repair_kind='restore exact author-reference apostrophe'
        elif '“' in target:corrupted=target.replace('“','"',1);repair_kind='restore exact author-reference quote'
        else:
            token=next(m for m in re.finditer(r'\b\w{5,}\b',target));corrupted=target[:token.start()]+token.group()+' '+target[token.start():];repair_kind='remove duplicate using explicit reference'
        variants=[('write','fiction',write_prompt(target,'science-fiction' if source.startswith('wells') else 'detective-fiction'),target,0,len(target)),('continue','fiction',f'Continue this prose fragment in at most {cap(tail)} words, retaining its narrator, voice and tense. Return only the next passage, without repeating the fragment or adding commentary.\n\nFRAGMENT:\n'+target[:cut].rstrip(),tail,cut,len(target)),('reference-repair','editing','Correct the draft to agree exactly with the AUTHOR REFERENCE. Preserve its facts, chronology, voice, spelling and every punctuation mark. Return only the corrected passage. Do not add an explanation.\n\nAUTHOR REFERENCE (read-only):\n'+target+'\n\nDRAFT TO CORRECT:\n'+corrupted,target,0,len(target))]
        for kind,task,prompt,answer,start,end in variants:
            ident=f'v2-new-{i:03d}-{kind}'
            assert target[start:end]==answer
            records.append(new_record(ident,task,prompt,answer,source,span,work))
            trace.append(dict(id=ident,source_span=span,target_start=start,target_end=end,transformed_excerpt_sha256=hashlib.sha256(target.encode()).hexdigest(),target_sha256=hashlib.sha256(answer.encode()).hexdigest(),kind=kind,constructed_repair=repair_kind if kind=='reference-repair' else None))
    rows(P/'records.jsonl',records);rows(P/'trace.jsonl',trace)
    valid=validate_dataset(P/'records.jsonl',LEDGER,['GB','US'])
    assert all(r['teacher'] is None and r['origin']=='derived' for r in valid)
    from collections import Counter
    report=dict(passed=True,records=len(valid),by_split=dict(Counter(r['split'] for r in valid)),training_by_task=dict(Counter(r['task'] for r in valid if r['split']=='train')),new_sources_paragraphs=16,human_quality_ratings=0,generated_literary_targets=0,training_authors=sorted({a for r in valid if r['split']=='train' for a in r['_author_ids']}),validation_authors=sorted({a for r in valid if r['split']=='validation' for a in r['_author_ids']}),limitations=['Anchored Write is source-conditioned reconstruction, not a fully original scene written to a semantic outline.','Reference repairs are mechanically constructed, not genuine author revisions.','Historical genres and small dataset remain inadequate to establish Muse equivalence.','Wray validation was used in previous exploratory project adapters, but is excluded from this candidate training.','Previous 24-case diagnostics are exposed development evidence; new evaluation must be separately frozen.'])
    with (P/'validation.json').open('x') as f:json.dump(report,f,indent=2)
    with (P/'TRAINING-REVIEW.md').open('x') as f:
        f.write('# Source-only curriculum v2 — AI audit, not human quality approval\n\n')
        for r in records:
            if r['split']=='train':f.write('## '+r['id']+'\n\n'+r['messages'][0]['content']+'\n\n**SOURCE ANSWER**\n\n'+r['messages'][-1]['content']+'\n\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

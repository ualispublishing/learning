import json,re,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RD=ROOT/'reading'; AUD=RD/'audit'
DIAC=re.compile('[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')

def norm(x,lang):
    x=unicodedata.normalize('NFC',x or '').strip().replace('\u0640','')
    if lang in ('arabic','urdu'): return DIAC.sub('',x)
    return x.replace('\u2019',"'").replace('\u2018',"'").casefold()

def passage_rows(lang):
    return [json.loads(x) for x in (RD/lang/'a1'/'passages.jsonl').read_text(encoding='utf-8').splitlines() if x]

def support_map(lang):
    data=json.loads((RD/'lexicons'/f'{lang}_a1_support.json').read_text(encoding='utf-8'))
    out={}
    for item in data['items']:
        for v in [item.get('lemma','')]+item.get('forms',[]):
            if v: out[norm(v,lang)]=item['id']
    return out

def parse_label(label,lang,cfg):
    parts=[x.strip() for x in label.split('|')]
    vals={norm(parts[0],lang)}
    for part in parts[1:]:
        if part.startswith('lemma='):
            lemma=part[6:].strip()
            lemma=cfg.get('lemma_aliases',{}).get(lemma,lemma)
            vals.add(norm(lemma,lang))
    return {x for x in vals if x}

def main():
    raw=json.loads((AUD/'a1_unit01_coverage_audit.json').read_text(encoding='utf-8'))
    aliases=json.loads((RD/'planning'/'a1_target_aliases.json').read_text(encoding='utf-8'))
    functions=json.loads((RD/'planning'/'a1_function_support.json').read_text(encoding='utf-8'))
    out={'version':1,'source_audit':'reading/audit/a1_unit01_coverage_audit.json','policy':'Unit-01 rank 1-500 prerequisite band; tail/outside items require target, verified support, grammar/function, or proper-name status','languages':{},'overall_gate':'PASS'}
    for lang,block in raw['languages'].items():
        pmap={p['id']:p for p in passage_rows(lang)}; sup=support_map(lang); cfg=functions[lang]
        func={norm(x,lang) for x in cfg.get('function_forms',[])}; proper={norm(x,lang) for x in cfg.get('proper_names',[])}
        seen_targets=set(); seen_support=set(); rows=[]; allbad=Counter()
        for diag in sorted(block['passages'],key=lambda x:x['sequence']):
            p=pmap[diag['id']]; current={x['id'] for x in p.get('new_lexical_targets',[])}; active=seen_targets|current
            current_alias={norm(v,lang) for tid in current for v in aliases.get(lang,{}).get(tid,[])}
            active_alias={norm(v,lang) for tid in active for v in aliases.get(lang,{}).get(tid,[])}
            used_support=set(); bad=Counter(); controlled=Counter()
            tail_total=sum(diag['band_counts'].get(k,0) for k in ('rank_501_1000','rank_1001_2000','rank_2001_3000'))
            outside_total=diag['band_counts'].get('outside_3000',0)
            tail_listed=outside_listed=0
            for label,count in diag['top_rank_gt_500_tokens']:
                tail_listed+=count; forms=parse_label(label,lang,cfg)
                if forms&proper: controlled['proper_name']+=count
                elif forms&current_alias: controlled['deliberate_target']+=count
                elif forms&active_alias: controlled['previous_target']+=count
                elif forms&set(sup):
                    hits={sup[x] for x in forms if x in sup}; used_support|=hits; controlled['verified_support']+=count
                elif forms&func: controlled['grammar_function']+=count
                else: bad['ranked_tail: '+label]+=count
            for label,count in diag['top_outside_3000_tokens']:
                outside_listed+=count; forms=parse_label(label,lang,cfg)
                if forms&proper: controlled['proper_name']+=count
                elif forms&current_alias: controlled['deliberate_target']+=count
                elif forms&active_alias: controlled['previous_target']+=count
                elif forms&set(sup):
                    hits={sup[x] for x in forms if x in sup}; used_support|=hits; controlled['verified_support']+=count
                elif forms&func: controlled['grammar_function']+=count
                else: bad['outside: '+label]+=count
            if tail_total>tail_listed: bad['unlisted ranked-tail diagnostic tokens']+=tail_total-tail_listed
            if outside_total>outside_listed: bad['unlisted outside-backbone diagnostic tokens']+=outside_total-outside_listed
            new_support=used_support-seen_support; max_support=2 if p['sequence']<=2 else 3 if p['sequence']<=5 else 0
            target_ok=(1<=len(current)<=2) if p['sequence']<=5 else len(current)==0
            support_ok=len(new_support)<=max_support; p6_ok=not(p['sequence']==6 and (current or new_support))
            gate='PASS' if not bad and target_ok and support_ok and p6_ok else 'REVIEW_REQUIRED'
            if gate!='PASS': out['overall_gate']='REVIEW_REQUIRED'
            allbad.update(bad)
            rows.append({'id':diag['id'],'sequence':p['sequence'],'diagnostic_inventory_3000_coverage':diag['inventory_3000_coverage'],'controlled_flagged_token_counts':dict(controlled),'uncontrolled':bad.most_common(),'new_target_ids':sorted(current),'verified_support_ids_used':sorted(used_support),'new_support_ids':sorted(new_support),'new_support_limit':max_support,'target_count_ok':target_ok,'support_count_ok':support_ok,'p6_no_new_material_ok':p6_ok,'gate':gate})
            seen_targets|=current; seen_support|=used_support
        out['languages'][lang]={'pass_count':sum(x['gate']=='PASS' for x in rows),'review_count':sum(x['gate']!='PASS' for x in rows),'top_uncontrolled':allbad.most_common(),'passages':rows}
    (AUD/'a1_unit01_supported_coverage_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'overall_gate':out['overall_gate'],'languages':{k:{'pass':v['pass_count'],'review':v['review_count'],'top':v['top_uncontrolled'][:12]} for k,v in out['languages'].items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Current 665-row Arabic phrase-bank semantic-fidelity audit.

Naturalness is audited separately. This pass checks the live schema, phrase/example
fidelity, translation completeness, and conservative English gloss/example support.
Flags are review signals only; this script never rewrites learner cards.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'; P=ROOT/'arabic_phrase_bank.csv'
EXPECTED=665
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')
AR=re.compile(r'[\u0621-\u064a]+'); LAT=re.compile(r'[A-Za-z]')
EN=re.compile(r'(?m)^EN:\s*(.+?)\s*$'); FR=re.compile(r'(?m)^FR:\s*(.+?)\s*$'); UR=re.compile(r'(?m)^UR:\s*(.+?)\s*$')
DEF=re.compile(r'(?ms)^Definition:\s*\n\(EN\)\s*(.+?)(?=\n\n(?:Example:|Translation:|Root:|Related / near-equivalents:)|\Z)')
EX=re.compile(r'(?m)^Example:\s*(.+?)\s*$'); XT=re.compile(r'(?m)^Translation:\s*(.+?)\s*$')
ROOT_RE=re.compile(r'(?m)^Root:\s*(.+?)\s*$'); REL=re.compile(r'(?m)^Related / near-equivalents:\s*(.+?)\s*$')
EW=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOP={'a','an','the','to','of','and','or','for','in','on','at','by','with','from','is','are','was','were','be','it','this','that','i','you','he','she','we','they','me','my','your','his','her','our','their'}

def grab(rx,s):
 m=rx.search(s or '');return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def norm_ar(s):
 s=DIAC.sub('',unicodedata.normalize('NFKC',s or '').replace('ـ',''))
 return ' '.join(AR.findall(s))
def stem(w):
 w=w.lower()
 for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
  if len(w)>len(suf)+3 and w.endswith(suf):return w[:-len(suf)]+('y' if suf=='ied' else '')
 return w
def words(s):return {stem(w) for w in EW.findall(s or '') if stem(w) not in STOP and len(stem(w))>=3}
def gloss_supported(gloss,translation):
 t=words(translation)
 for alt in re.split(r'\s*(?:/|;|,)\s*',gloss or ''):
  a=words(alt)
  if a and a&t:return True
 return False

def main():
 with P.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 groups=defaultdict(list)
 for i,r in enumerate(rows,1):groups[norm_ar(r.get('Front',''))].append(i)
 dup={k:v for k,v in groups.items() if k and len(v)>1}
 out=[];counts=Counter()
 for i,r in enumerate(rows,1):
  front=(r.get('Front') or '').strip();back=r.get('Back') or ''
  en,fr,ur=grab(EN,back),grab(FR,back),grab(UR,back);definition=grab(DEF,back)
  ex,xt=grab(EX,back),grab(XT,back);root,rel=grab(ROOT_RE,back),grab(REL,back)
  nf,ne=norm_ar(front),norm_ar(ex);flags=[]
  required={'missing_en':en,'missing_fr':fr,'missing_ur':ur,'missing_definition_en':definition,'missing_example_ar':ex,'missing_example_en':xt,'missing_root':root,'missing_related':rel}
  for code,val in required.items():
   if not val:flags.append(code)
  if nf in dup:flags.append('normalized_duplicate_front')
  if front and not AR.search(front):flags.append('no_arabic_front')
  if en and not LAT.search(en):flags.append('bad_en_script')
  if fr and not LAT.search(fr):flags.append('bad_fr_script')
  if ur and not AR.search(ur):flags.append('bad_ur_script')
  instantiated=bool(nf and ne and nf in ne)
  supported=gloss_supported(en,xt) if en and xt else False
  if ex and nf and not instantiated:flags.append('front_not_instantiated_in_example')
  if en and xt and not supported:flags.append('english_gloss_not_visible_in_example_translation')
  status='explicit_review_required' if flags else 'verified';counts[status]+=1
  out.append({'rank':i,'front':front,'en':en,'fr':fr,'ur':ur,'definition_en':definition,'example_ar':ex,'example_en':xt,'front_in_example':instantiated,'english_gloss_example_support':supported,'flags':'|'.join(flags),'status':status})
 fields=list(out[0])
 with (AUDIT/'arabic_phrase_bank_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
 review=[x for x in out if x['status']=='explicit_review_required']
 with (AUDIT/'arabic_phrase_bank_review_queue.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(review)
 flags=Counter()
 for x in out:
  for y in filter(None,x['flags'].split('|')):flags[y]+=1
 summary={'file':'arabic_phrase_bank.csv','rows':len(rows),'expected_rows':EXPECTED,'distinct_normalized_fronts':len(groups),'normalized_duplicate_groups':len(dup),'verified_rows':counts['verified'],'review_rows':len(review),'flag_counts':dict(flags),'front_instantiated_in_example':sum(x['front_in_example'] for x in out),'english_gloss_example_supported':sum(x['english_gloss_example_support'] for x in out),'promotion_gate':'PASS' if len(rows)==EXPECTED and not review else 'REVIEW_REQUIRED','policy':'Phrase/example and English gloss/example checks are conservative triage signals; flagged rows require manual educator review and are never auto-deleted.'}
 (AUDIT/'arabic_phrase_bank_audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

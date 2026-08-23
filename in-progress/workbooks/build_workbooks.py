#!/usr/bin/env python3
from __future__ import annotations

import csv, html, json, re, shutil, unicodedata, zipfile
from pathlib import Path
from urllib.request import Request, urlopen

from pypdf import PdfReader
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "in-progress" / "workbooks" / "build-output"
SRC = OUT / "source-cache"
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

LANGS = {
    "arabic": {"code":"ara","name":"Arabic","target":"العربية","dir":"rtl","font":"Noto Naskh Arabic","vocab":ROOT/"arabic_top1000.csv","zip":"https://mail.manythings.org/anki/ara-eng.zip","txt":"ara.txt","script":"arabic"},
    "urdu": {"code":"urd","name":"Urdu","target":"اردو","dir":"rtl","font":"Noto Nastaliq Urdu","vocab":ROOT/"urdu_top1000.csv","zip":"https://mail.manythings.org/anki/urd-eng.zip","txt":"urd.txt","script":"arabic"},
    "french": {"code":"fra","name":"French","target":"Français","dir":"ltr","font":"DejaVu Sans","vocab":ROOT/"french_top1000.csv","zip":"https://mail.manythings.org/anki/fra-eng.zip","txt":"fra.txt","script":"latin"},
}
BAD_EN={"tom","mary","boston","tokyo","paris","london","john","jack","jim","bob","war","gun","kill","killed","murder","sex","porn","drunk","suicide"}
CONV={"i","you","we","me","my","your","our","please","thanks","thank","sorry","excuse","what","where","when","why","how","who","which","can","could","would","do","did","are","is","have","want","need","like","know","think","feel","go","come","help","tell","say","speak","understand","wait","call","eat","drink","buy","pay","home","work","school","today","tomorrow","time","bus","train","store","shop"}

FOUNDATIONS={
"arabic":[
("Writing system","Arabic is written from right to left. Letters usually join within a word, and their shapes change with position. Practice whole connected words rather than isolated glyphs once the basic forms are familiar."),
("Vowels","Long vowels are commonly written with ا, و, and ي. Short vowels may be shown with diacritics in beginner material but are usually omitted in ordinary text; use context, morphology, and vocabulary knowledge to recover them."),
("MSA scope","This workbook targets Modern Standard Arabic (MSA). It avoids deliberately dialect-specific forms in the core explanations; spoken varieties differ by region and should be learned as a separate layer."),
("Definiteness","The definite article is ال. With the traditional sun letters, the /l/ assimilates in pronunciation while the spelling remains ال, as in الشمس."),
("Gender and agreement","Nouns are grammatically masculine or feminine. Adjectives normally follow the noun and agree with it in definiteness, gender, number, and case where case endings are expressed."),
("Nominal and verbal sentences","A present-tense nominal sentence can link a subject and predicate without an overt equivalent of English 'is'. Verbal sentences use a conjugated verb and show person/number/gender distinctions."),
("Word order","Both verb-subject-object and subject-verb-object orders occur in MSA. Agreement patterns can differ depending on whether a plural subject follows or precedes the verb."),
("Study method","Read the target text first, cover the English meaning, reproduce it from memory, then check. Revisit missed items with spacing rather than copying the answer repeatedly."),
],
"urdu":[
("Writing system","Urdu is written from right to left in a Perso-Arabic script, commonly in Nastaliq style. Letter shapes connect and stack; handwriting practice should focus on connected words and consistent baseline flow."),
("Sounds and spelling","Urdu uses additional letters and digraph conventions for sounds not found in Arabic or Persian, including retroflex and aspirated consonants. Short vowels are often not marked in ordinary text."),
("Word order","Neutral Urdu word order is usually subject-object-verb. Postpositions follow noun phrases, so learners should practice whole chunks rather than translating English word by word."),
("Gender and agreement","Nouns have grammatical gender. Adjectives and verbs can change form for gender and number; agreement also interacts with tense/aspect and postpositions."),
("Respect and pronouns","آپ is the normal respectful/formal second-person pronoun and takes plural-style agreement. تم is familiar; تو is highly intimate and can sound rude outside close relationships."),
("Izafat","The izafat construction links nouns and adjectives in many Persian-derived expressions. Its written and spoken realization depends on the final sound and orthography of the first word."),
("Verb building","Many common predicates combine a noun/adjective with ہونا 'to be/become' or a light verb. Learn these combinations as units because literal word-by-word translation is often misleading."),
("Study method","Read the Urdu first, cover the English, say or write the meaning from memory, then check. Recycle missed items after a delay and mix old material with new material."),
],
"french":[
("Writing system","French uses the 26-letter Latin alphabet. Accents and the cedilla are meaningful spelling marks: é, è, ê, ë, à, â, î, ï, ô, ö, ù, û, ü, and ç occur in standard writing."),
("Gender and articles","French nouns are grammatically masculine or feminine. Learn each noun with an article when possible: un/une, le/la, or l'. Plural definite and indefinite articles are les and des."),
("Elision","Before a vowel sound or mute h, certain short words elide: le/la -> l', je -> j', de -> d', and ne -> n'. This is part of standard written French, not an optional pronunciation shortcut."),
("Agreement","Many adjectives agree in gender and number with the noun they modify. Past participle agreement follows specific rules; do not assume every final -e or -s is pronounced."),
("Questions","Common question patterns include intonation in speech, est-ce que + clause, and inversion in formal styles. Question words include qui, que/quoi, où, quand, pourquoi, and comment."),
("Negation","Standard written negation commonly surrounds a conjugated verb with ne ... pas. In everyday speech, ne is often omitted, but learners should recognize and be able to produce the standard form."),
("Core time frames","Prioritize the present, passé composé for many completed past events, imparfait for background/habitual past, and futur proche for near-future plans before expanding to less frequent forms."),
("Study method","Read the French first, cover the English, retrieve the meaning, then reproduce the French. For pronunciation, shadow reliable native audio rather than relying on ad-hoc English-style respelling."),
]}

def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().strip(); s=re.sub(r"[\s\u200c\u200d]+"," ",s)
    return re.sub(r"[^\w\u0600-\u06ffà-ÿ'’-]+","",s,flags=re.I)

def download(url,path):
    if path.exists() and path.stat().st_size>1000:return
    req=Request(url,headers={"User-Agent":"learning-workbook-builder/1.0"})
    with urlopen(req,timeout=90) as r,open(path,"wb") as f:shutil.copyfileobj(r,f)

def parse_vocab(path):
    out=[]
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            front=(row.get("Front") or "").strip(); back=(row.get("Back") or "").strip()
            m=re.search(r"(?:^|\n)Meaning:\s*(.+?)(?:\n\n|$)",back,flags=re.S); meaning=m.group(1).strip() if m else ""
            rr=re.search(r"(?:^|\n)Rank:\s*(\d+)",back); rank=int(rr.group(1)) if rr else len(out)+1
            if front and meaning:out.append({"rank":rank,"target":front,"english":meaning})
    out.sort(key=lambda x:x["rank"])
    if len(out)!=1000:raise SystemExit(f"{path.name}: expected 1000 vocabulary rows, got {len(out)}")
    if len({norm(x['target']) for x in out})!=1000:raise SystemExit(f"{path.name}: vocabulary duplicates after normalization")
    if any(re.search(r"review\s*index|usage\s*\d+",x['target']+' '+x['english'],re.I) for x in out):raise SystemExit(f"{path.name}: padded/review vocabulary detected")
    return out

def english_words(s):return re.findall(r"[A-Za-z']+",s.casefold())
def conversation_score(en):
    w=english_words(en); st=set(w); n=len(w); score=5*len(st&CONV)
    if "?" in en:score+=8
    if "!" in en:score+=2
    if 3<=n<=10:score+=6
    elif n<=14:score+=2
    else:score-=(n-14)*1.5
    if st&BAD_EN:score-=50
    if re.search(r"\b[A-Z][a-z]{2,}\b",en[1:]):score-=4
    if re.search(r"https?://|www\.|\d{4}",en):score-=25
    return score

def script_ratio(s,which):
    letters=[c for c in s if c.isalpha()]
    if not letters:return 0.0
    if which=="arabic":good=sum(1 for c in letters if '\u0600'<=c<='\u06ff' or '\u0750'<=c<='\u077f' or '\u08a0'<=c<='\u08ff')
    else:good=sum(1 for c in letters if 'a'<=c.casefold()<='z' or '\u00c0'<=c<='\u024f')
    return good/len(letters)

def parse_sentences(cfg):
    z=SRC/f"{cfg['code']}-eng.zip"; download(cfg['zip'],z)
    with zipfile.ZipFile(z) as zz:raw=zz.read(cfg['txt']).decode("utf-8-sig")
    rows=[]; seen_t=set(); seen_e=set()
    for line in raw.splitlines():
        parts=line.split("\t")
        if len(parts)<3:continue
        en,target,attr=parts[0].strip(),parts[1].strip(),parts[2].strip(); nt,ne=norm(target),norm(en)
        if not nt or not ne or nt in seen_t or ne in seen_e:continue
        if "CC-BY 2.0" not in attr or "tatoeba.org" not in attr:continue
        if script_ratio(target,cfg['script'])<.65:continue
        if len(english_words(en))<2 or len(english_words(en))>18 or len(target)>180 or len(en)>180:continue
        seen_t.add(nt);seen_e.add(ne);rows.append({"target":target,"english":en,"attribution":attr,"score":conversation_score(en)})
    if len(rows)<1000:raise SystemExit(f"{cfg['name']}: only {len(rows)} unique licensed sentence pairs after safety filters")
    rows=sorted(rows,key=lambda x:(-x['score'],len(english_words(x['english'])),x['english']))[:1000]
    rows.sort(key=lambda x:(len(english_words(x['english'])),-x['score'],x['english']))
    for i,r in enumerate(rows,1):r['rank']=i
    if len({norm(r['target']) for r in rows})!=1000 or len({norm(r['english']) for r in rows})!=1000:raise SystemExit(f"{cfg['name']}: sentence duplicate gate failed")
    return rows

def esc(s):return html.escape(s,quote=False)
CSS='''@page { size: Letter; margin: .58in .62in .62in .62in; @bottom-center { content: counter(page); font: 8pt "DejaVu Sans"; color:#666; } } @page :first { @bottom-center { content:none; } } *{box-sizing:border-box} body{font-family:"DejaVu Sans",sans-serif;color:#18212b;font-size:10.2pt;line-height:1.38} h1,h2,h3{break-after:avoid;color:#17324d} h1{font-size:28pt;margin:0 0 .18in} h2{font-size:18pt;border-bottom:1.5pt solid #b8c9d8;padding-bottom:5pt;margin:.18in 0 .12in} h3{font-size:12.5pt;margin:.12in 0 .04in}.cover{break-after:page;padding-top:1.15in}.kicker{text-transform:uppercase;letter-spacing:1.4pt;font-size:8.5pt;color:#5b7185;font-weight:700}.subtitle{font-size:13pt;color:#475c6e;max-width:6.3in}.claim{margin-top:.25in;padding:.16in .2in;background:#f2f6f9;border-left:4pt solid #7da1bd}.toc{break-after:page}.toc a{color:#17324d;text-decoration:none}.toc a::after{content:leader('.') target-counter(attr(href),page)}.section-start{break-before:page}.target{font-family:var(--target-font);font-size:16pt;font-weight:600;line-height:1.55}.rtl{direction:rtl;text-align:right;unicode-bidi:plaintext}.entry{break-inside:avoid;border:1px solid #d9e2ea;border-radius:5px;padding:7pt 9pt;margin:0 0 7pt}.entry .num{float:right;font-size:8pt;color:#6d7d89;font-family:"DejaVu Sans"}.rtl.entry .num{float:left}.meaning{margin-top:2pt;color:#34495a}.attrib{margin-top:3pt;font-size:6.6pt;color:#75828c;font-family:"DejaVu Sans";direction:ltr;text-align:left}.write{border-bottom:.7pt solid #bfcad2;height:17pt;margin-top:3pt}.vocab-grid{column-count:2;column-gap:10pt}.vocab-grid .entry{display:inline-block;width:100%}.note{font-size:8.5pt;color:#5c6d79}.license{font-size:8.5pt}.foundation-card{break-inside:avoid;padding:9pt 11pt;margin:0 0 8pt;background:#f6f8fa;border-left:3pt solid #7b9bb5}'''

def cover(cfg,segment="Complete master"):
    return f'''<section class="cover"><div class="kicker">Version 1.0 production candidate</div><h1>{esc(cfg['name'])} Workbook</h1><div class="target {'rtl' if cfg['dir']=='rtl' else ''}" style="--target-font:'{cfg['font']}'">{esc(cfg['target'])}</div><p class="subtitle">Writing foundations, core grammar, 1,000 distinct canonical vocabulary entries, and 1,000 distinct bilingual practice sentences with handwriting/retrieval space.</p><div class="claim"><strong>{esc(segment)}</strong><br>Built from the learning repository's audited top-1,000 vocabulary deck and a separately selected, attributed sentence corpus. Transliteration is intentionally omitted from sentence drills to avoid teaching inconsistent ad-hoc romanization.</div></section>'''
def foundations_html(lang,cfg):
    cards=''.join(f'<div class="foundation-card"><h3>{esc(t)}</h3><p>{esc(b)}</p></div>' for t,b in FOUNDATIONS[lang]); note="MSA is the target register throughout this workbook." if lang=="arabic" else "Standard Urdu in Nastaliq is the target register throughout this workbook." if lang=="urdu" else "Contemporary standard French is the target register throughout this workbook."
    return f'''<section id="foundations"><h2>Foundations</h2><p class="note">{esc(note)} These pages are intentionally concise: they orient practice, while the vocabulary and sentence sections provide the bulk of retrieval work.</p>{cards}<h3>Handwriting warm-up</h3><p>Copy five useful words from today's lesson, then write them again from memory.</p>{'<div class="write"></div>'*8}</section>'''
def vocab_html(vocab,cfg,start=1,end=1000,heading=None):
    rows=[]
    for r in vocab[start-1:end]:
        rtl='rtl' if cfg['dir']=='rtl' else ''; rows.append(f'''<div class="entry {rtl}"><span class="num">{r['rank']}</span><div class="target" style="--target-font:'{cfg['font']}'">{esc(r['target'])}</div><div class="meaning" dir="ltr">{esc(r['english'])}</div><div class="write"></div></div>''')
    return f'''<section id="vocab-{start}" class="section-start"><h2>{esc(heading or f'Vocabulary {start}-{end}')}</h2><p class="note">Cover the meaning, retrieve it, then write the target word from memory. The 1,000 entries are distinct after Unicode normalization.</p><div class="vocab-grid">{''.join(rows)}</div></section>'''
def sentences_html(rows,cfg,start=1,end=1000,heading=None):
    out=[]
    for r in rows[start-1:end]:
        rtl='rtl' if cfg['dir']=='rtl' else ''; out.append(f'''<div class="entry {rtl}"><span class="num">{r['rank']}</span><div class="target" style="--target-font:'{cfg['font']}'">{esc(r['target'])}</div><div class="meaning" dir="ltr">{esc(r['english'])}</div><div class="attrib">{esc(r['attribution'])}</div><div class="write"></div><div class="write"></div></div>''')
    return f'''<section id="sent-{start}" class="section-start"><h2>{esc(heading or f'Practice sentences {start}-{end}')}</h2><p class="note">Read the target sentence, cover the English, retrieve the meaning, then reproduce the target sentence. Items are ordered broadly from shorter to longer after usefulness filtering.</p>{''.join(out)}</section>'''
def license_html(cfg):
    return '''<section class="section-start license"><h2>Sources, licensing, and QA scope</h2><p><strong>Vocabulary:</strong> drawn from this repository's canonical top-1,000 deck for the language. The repository's source and audit records remain the source of truth.</p><p><strong>Sentences:</strong> selected from the ManyThings bilingual exports of the Tatoeba Project. Each sentence entry retains the supplied sentence-level attribution. Tatoeba textual data is distributed under CC BY 2.0 France; the exact attribution line is printed with each redistributed pair.</p><p><strong>Quality statement:</strong> automated release gates check row counts, normalized uniqueness, script plausibility, attribution presence, PDF generation, and rendering prerequisites. These checks reduce risk but are not a substitute for independent native-speaker editorial certification. No claim of absolute error-free linguistic correctness is made.</p></section>'''
def html_doc(cfg,body):return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'''
def render(path,cfg,body):
    HTML(string=html_doc(cfg,body),base_url=str(ROOT)).write_pdf(path)
    if path.stat().st_size<10000:raise SystemExit(f"PDF too small: {path}")
def write_csv(path,rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["rank","target","english","attribution"]);w.writeheader()
        for r in rows:w.writerow({k:r.get(k,"") for k in w.fieldnames})
def pdf_stats(path):
    r=PdfReader(str(path));return {"pages":len(r.pages),"bytes":path.stat().st_size}
def build_lang(lang,cfg):
    langout=OUT/lang;langout.mkdir(parents=True,exist_ok=True);vocab=parse_vocab(cfg['vocab']);sent=parse_sentences(cfg);write_csv(langout/f"{lang}_sentence_bank_1000.csv",sent)
    segments=[("01_foundations",cover(cfg,"Foundations")+foundations_html(lang,cfg)+license_html(cfg)),("02_vocabulary_001-500",cover(cfg,"Vocabulary 1-500")+vocab_html(vocab,cfg,1,500)+license_html(cfg)),("03_vocabulary_501-1000",cover(cfg,"Vocabulary 501-1000")+vocab_html(vocab,cfg,501,1000)+license_html(cfg))]
    for a,b,n in [(1,250,4),(251,500,5),(501,750,6),(751,1000,7)]:segments.append((f"0{n}_sentences_{a:03d}-{b:04d}",cover(cfg,f"Sentences {a}-{b}")+sentences_html(sent,cfg,a,b)+license_html(cfg)))
    files=[]
    for stem,body in segments:
        p=langout/f"{stem}.pdf";render(p,cfg,body);files.append(p)
    master=langout/f"00_{lang}_complete_master.pdf";toc='''<section class="toc"><h2>Contents</h2><p><a href="#foundations">Foundations</a></p><p><a href="#vocab-1">Vocabulary 1-500</a></p><p><a href="#vocab-501">Vocabulary 501-1000</a></p><p><a href="#sent-1">Sentences 1-250</a></p><p><a href="#sent-251">Sentences 251-500</a></p><p><a href="#sent-501">Sentences 501-750</a></p><p><a href="#sent-751">Sentences 751-1000</a></p></section>'''
    mb=cover(cfg,"Complete master")+toc+foundations_html(lang,cfg)+vocab_html(vocab,cfg,1,500)+vocab_html(vocab,cfg,501,1000)+sentences_html(sent,cfg,1,250)+sentences_html(sent,cfg,251,500)+sentences_html(sent,cfg,501,750)+sentences_html(sent,cfg,751,1000)+license_html(cfg);render(master,cfg,mb);files.insert(0,master)
    qa={"language":lang,"vocabulary_rows":len(vocab),"vocabulary_unique":len({norm(x['target']) for x in vocab}),"sentence_rows":len(sent),"sentence_target_unique":len({norm(x['target']) for x in sent}),"sentence_english_unique":len({norm(x['english']) for x in sent}),"sentence_attribution_rows":sum(1 for x in sent if 'CC-BY 2.0' in x['attribution'] and 'tatoeba.org' in x['attribution']),"sentence_question_count":sum('?' in x['english'] for x in sent),"sentence_avg_english_words":round(sum(len(english_words(x['english'])) for x in sent)/1000,2),"pdfs":{p.name:pdf_stats(p) for p in files},"status":"PASS"};(langout/f"{lang}_qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8");return qa
def main():
    allqa={}
    for lang,cfg in LANGS.items():print(f"Building {lang}...",flush=True);allqa[lang]=build_lang(lang,cfg)
    (OUT/"qa_summary.json").write_text(json.dumps(allqa,ensure_ascii=False,indent=2),encoding="utf-8")
    md=["# Workbook V1 production QA summary","","Automated gates passed for the generated candidate files. This is not an absolute linguistic correctness guarantee; independent native-speaker editorial review remains the final commercial-certification step.",""]
    for lang,q in allqa.items():md += [f"## {lang.title()}",f"- Vocabulary: {q['vocabulary_rows']} rows / {q['vocabulary_unique']} normalized unique",f"- Sentences: {q['sentence_rows']} rows / {q['sentence_target_unique']} target unique / {q['sentence_english_unique']} English unique",f"- Attributed sentence rows: {q['sentence_attribution_rows']}",f"- PDFs generated: {len(q['pdfs'])}",""]
    (OUT/"QA_REPORT.md").write_text("\n".join(md),encoding="utf-8");print(json.dumps(allqa,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

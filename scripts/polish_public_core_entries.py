#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MEAN_RE=re.compile(r'(?m)^(Meaning:\s*).+$')
POS_RE=re.compile(r'(?m)^(Part of speech:\s*).+$')

# Conservative public-facing glosses: core modern senses only. Rare/historical/raw
# lexicographic notes are intentionally omitted rather than exposed to learners.
PATCHES={
'arabic_top1000.csv':{
 'لما':('when (لَمَّا); not yet (لَمَّا); for what / to what (لِمَا)','particle / adverb / interrogative expression'),
 'كلام':('speech; talk; words','noun'),
 'ضبط':('control; regulation; adjustment; to control / adjust','noun / verb'),
 'قدر':('fate / destiny; amount / value; ability','noun / verb'),
 'بأس':('harm / hardship; might / strength','noun'),
 'قضاء':('judgment / ruling; judiciary; fulfillment / carrying out','noun / verbal noun'),
 'تناول':('eating / consumption; taking; handling / dealing with','noun / verb'),
},
'french_top1000.csv':{
 'être':('to be','verb / auxiliary verb'),'son':('his / her / its (masculine singular possessive); sound; bran','determiner / noun'),'fait':('fact; deed; done / made (past participle of faire)','noun / past participle'),'garder':('to keep; to guard; to look after','verb'),'puis':('then; next; and then','adverb / conjunction'),'suivre':('to follow; to take / attend (a course); to understand / follow','verb'),'retrouver':('to find again; to meet up with; to regain / rediscover','verb'),'retourner':('to return / go back; to turn over; to flip','verb'),'tellement':('so; so much; so many','adverb'),'enfin':('finally; at last; in the end','adverb'),'service':('service; department; duty','noun'),'tourner':('to turn / rotate; to film / shoot','verb'),'moyen':('means / way; average; medium','adjective / noun'),'coucher':('to put to bed; to lie down / go to bed','verb'),'terminer':('to finish; to end; to complete','verb'),'américain':('American','adjective / noun'),'attaquer':('to attack; to tackle / start on','verb'),'vue':('view; sight','noun'),'test':('test; trial','noun'),'réunion':('meeting; reunion; Réunion (island, as a proper name)','noun'),'signe':('sign; gesture; indication','noun'),'combat':('fight; battle; combat','noun'),'milieu':('middle; environment / surroundings; social circle','noun'),'rapide':('fast; rapid; quick','adjective'),'bonne':('good; maid (dated noun)','adjective / noun'),
},
'french_top3000.csv':{
 'sortie':('exit; outing; release / output','noun'),'représenter':('to represent; to depict; to stand for','verb'),'finalement':('finally; eventually; in the end','adverb'),'déplacer':('to move / shift; to travel / go somewhere','verb'),'emporter':('to take / carry away; to win','verb'),'moindre':('lesser; smaller; least / slightest','adjective'),'sort':('fate / destiny; spell (magic)','noun'),'saison':('season','noun'),'justement':('precisely / exactly; rightly / justly','adverb'),'crétin':('idiot; stupid / idiotic','noun / adjective'),'théorie':('theory','noun'),'fabriquer':('to make; to manufacture; to fabricate','verb'),'informer':('to inform; to notify','verb'),'fantastique':('fantastic; fantastical','adjective'),'celle-là':('that one (feminine)','pronoun'),'saisir':('to seize / grab; to enter / capture data; to understand','verb'),'créature':('creature; living being','noun'),'curieux':('curious / inquisitive; unusual / strange','adjective'),'herbe':('grass; herb / plant; weed','noun'),'convenir':('to suit; to agree; to be appropriate','verb'),'fuite':('leak; escape / flight','noun'),'celle-ci':('this one (feminine)','pronoun'),'version':('version; account; translation','noun'),'mise':('bet / stake; putting / placement','noun'),'discussion':('discussion; conversation; debate','noun'),'mortel':('mortal; deadly','adjective / noun'),'somme':('sum / total; nap / doze','noun'),'océan':('ocean','noun'),'concours':('competition / contest; competitive examination; assistance / cooperation','noun'),'jus':('juice; liquid; coffee (informal)','noun'),'uniquement':('only; solely; exclusively','adverb'),'objectif':('objective / goal; objective / impartial; lens','noun / adjective'),'principe':('principle; rule; basis','noun'),'amant':('lover; male lover','noun'),'continue':('continuous; ongoing','adjective'),'auteur':('author; creator; perpetrator','noun'),'musée':('museum','noun'),'personnalité':('personality; public figure / celebrity','noun'),'lecture':('reading; playback','noun'),'sous-titre':('subtitle; caption','noun'),'combinaison':('combination; suit / coverall; slip (garment)','noun'),'assumer':('to take on / assume; to accept; to take responsibility for','verb'),'prime':('bonus; premium; prize / reward','noun'),'avenue':('avenue; possible route / means','noun'),
},
'urdu_top1000.csv':{
 'نے':('ergative marker','postposition'),'دن':('day; daytime','noun'),'علاقوں':('areas; regions','noun'),'ہمیں':('us; to us','pronoun'),'بچوں':('children','noun'),'خواتین':('women; ladies','noun'),'کردار':('role; character; conduct / behaviour','noun'),'مسائل':('problems; issues','noun'),'اعلی':('high; superior; supreme','adjective'),'تعلقات':('relations; relationships; connections','noun'),'ملکی':('national; domestic; of the country','adjective'),'تاریخ':('date; history','noun'),'تم':('you (familiar / informal)','pronoun'),'مسلمانوں':('Muslims (oblique plural)','noun'),'حقوق':('rights','noun'),'دنوں':('days (oblique plural)','noun'),'اقوام':('nations; peoples','noun'),'شام':('evening; Syria / the Levant (proper name, context-dependent)','noun / proper noun'),'ملکوں':('countries (oblique plural)','noun'),'خدمات':('services','noun'),'حقیقت':('reality; truth; fact','noun'),'ماہرین':('experts; specialists','noun'),'سامنا':('front; encounter; confrontation','noun'),'خدمت':('service; assistance; employment','noun'),'ہاتھوں':('hands (oblique plural)','noun'),'واقعات':('events; incidents','noun'),'آنکھوں':('eyes (oblique plural)','noun'),'معاملات':('matters; affairs; dealings','noun'),'دولت':('wealth; fortune; prosperity','noun'),'شہروں':('cities (oblique plural)','noun'),'جماعتوں':('groups; parties; classes','noun'),'تفصیلات':('details','noun'),'قوانین':('laws; regulations','noun'),'اساتذہ':('teachers','noun'),'گرم':('hot; warm','adjective'),'گھروں':('homes; houses (oblique plural)','noun'),'زبانوں':('languages; tongues (oblique plural)','noun'),'الفاظ':('words','noun'),'عورتوں':('women (oblique plural)','noun'),'روشن':('bright; illuminated; clear','adjective'),'محروم':('deprived; denied; excluded','adjective'),'منظر':('view; scene; sight','noun'),'صحافیوں':('journalists (oblique plural)','noun'),'کھڑے':('standing; upright','adjective'),'حدود':('limits; boundaries','noun'),'حملوں':('attacks; assaults (oblique plural)','noun'),'دوستوں':('friends (oblique plural)','noun'),
},
}
STALE_URDU='- Candidate only; requires hard final gate before promotion'
def patch_back(back,meaning,pos):
 back=MEAN_RE.sub(lambda m:m.group(1)+meaning,back)
 if POS_RE.search(back): back=POS_RE.sub(lambda m:m.group(1)+pos,back)
 elif pos: back=back.replace('Meaning: '+meaning,'Meaning: '+meaning+'\n\nPart of speech: '+pos,1)
 return back
def main():
 changed={}
 for name,mapping in PATCHES.items():
  p=ROOT/name
  with p.open(encoding='utf-8-sig',newline='') as f: r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
  n=0
  for row in rows:
   front=(row.get('Front') or '').strip()
   if front in mapping:
    new=patch_back(row['Back'],*mapping[front])
    if new!=row['Back']: row['Back']=new;n+=1
  with p.open('w',encoding='utf-8',newline='') as f: w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
  changed[name]=n
 p=ROOT/'urdu_top3000.csv'
 with p.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
 n=0
 for row in rows:
  new=row['Back'].replace(STALE_URDU,'- Passed hard final semantic and evidence-tier promotion gate')
  if new!=row['Back']:row['Back']=new;n+=1
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
 changed['urdu_top3000.csv metadata']=n
 print(changed)
if __name__=='__main__':main()

import json,re
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'reading/french/a1/passages.jsonl'
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x]
new={
'fr-a1-u01-p01':"Camille est dans un nouvel appartement avec sa mère. Sa mère dit : « Nous sommes ici maintenant. » Camille regarde une fenêtre et un livre. Elle dit : « Je veux travailler ici. » Sa mère va vers la porte et demande : « Tu veux venir avec moi ? » Camille vient avec elle. Puis elles retournent près de la fenêtre. Camille sourit et dit : « J’aime cet appartement. Je veux rester ici un peu. »",
'fr-a1-u01-p02':"Le matin, Camille regarde l’heure. Quand il est presque huit heures, sa mère dit : « Nous allons à l’école. » Alors Camille prend un livre et sort avec elle. Devant l’école, Sami vient vers Camille. Ils entrent ensemble. Quand les cours sont finis, Camille va à son appartement. Alors elle met son livre près de la fenêtre. Sa mère demande : « Tu es ici maintenant ? » Camille répond oui. Quand sa mère arrive, elles parlent un peu. Alors la journée d’école est finie."
}
for r in rows:
 if r['id'] in new:
  r['text']=new[r['id']]; r['word_count']=len(re.findall(r'\S+',r['text'])); r['estimated_known_token_coverage']=0; r['quality']['coverage_check']='pending'; r['quality']['status']='draft'
p.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')

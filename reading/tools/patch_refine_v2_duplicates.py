from pathlib import Path
p=Path('reading/tools/refine_french_a1_a2_metalinguistic_repair_v2.py')
s=p.read_text(encoding='utf-8')
old="""extra=[]; rec=idx['fr-a1-u08-p02']; q6=next(q for q in rec['questions'] if q['id']=='q6'); a6=next(a for a in rec['answer_key'] if a['id']=='a6')
assert q6['prompt']=='Que signifie « corps » ?' and a6['answer']=='L’ensemble physique d’une personne.'
q6['type']='vocabulary_in_context'; q6['prompt']='Dans « écouter son corps », que doit faire Camille ?'; a6['answer']='Elle doit faire attention à ce qu’elle ressent physiquement.'
changed.add(rec['id']); extra.append({'passage_id':rec['id'],'question_id':'q6','category':'preexisting_exact_duplicate_prompt','before':'Que signifie « corps » ?','after':q6['prompt']})
"""
new="""extra=[]
def repair_extra(rid,qid,expected_prompt,expected_answer,new_type,new_prompt,new_answer):
 rec=idx[rid]; q=next(x for x in rec['questions'] if x['id']==qid); a=next(x for x in rec['answer_key'] if x['id']==q['answer_id'])
 assert q['prompt']==expected_prompt and a['answer']==expected_answer,(rid,qid,'duplicate source drift',q['prompt'],a['answer'])
 q['type']=new_type; q['prompt']=new_prompt; a['answer']=new_answer; changed.add(rid)
 extra.append({'passage_id':rid,'question_id':qid,'category':'preexisting_exact_duplicate_prompt','before':expected_prompt,'after':new_prompt})
repair_extra('fr-a1-u08-p02','q6','Que signifie « corps » ?','L’ensemble physique d’une personne.','vocabulary_in_context','Dans « écouter son corps », que doit faire Camille ?','Elle doit faire attention à ce qu’elle ressent physiquement.')
repair_extra('fr-a1-u08-p03','q6','Que signifie « boire » ?','Prendre un liquide par la bouche.','grammar_choice','Choisis la phrase correcte : « il faut boire de l’eau » ou « il faut boit de l’eau » ?','« il faut boire de l’eau ».')
repair_extra('fr-a1-u08-p04','q6','Que signifie « dormir » ?','Être endormi, se reposer pendant le sommeil.','grammar_choice','Choisis la phrase correcte : « je vais dormir » ou « je vais dors » ?','« je vais dormir ».')
repair_extra('fr-a1-u09-p02','q6','Que signifie « ami » ?','Une personne avec qui on a une relation amicale.','grammar_choice','Choisis la forme correcte : « Sami est un ami de Camille » ou « Sami est une ami de Camille » ?','« Sami est un ami de Camille ».')
repair_extra('fr-a1-u09-p05','q6','Que signifie « travail » ici ?','Une tâche ou une activité à accomplir.','grammar_choice','Choisis la forme correcte : « un travail court » ou « une travail courte » ?','« un travail court ».')
repair_extra('fr-a1-u10-p03','q6','Que signifie « prix » ?','Le coût d’un produit ou d’un service.','grammar_choice','Choisis la forme correcte : « le prix du livre » ou « la prix du livre » ?','« le prix du livre ».')
repair_extra('fr-a1-u10-p05','q6','Que signifie « chaussure » ?','Un objet que l’on porte au pied pour le protéger.','grammar_choice','Choisis la forme correcte : « une chaussure » ou « un chaussure » ?','« une chaussure ».')
"""
assert old in s,'expected v2 duplicate-repair block not found'
s=s.replace(old,new,1)
# The phrase "Quel rôle joue..." is not itself grammatical metalanguage. Three A2 false
# positives were already semantically adjudicated: programme purpose, pourtant discourse
# effect, and the practical effect of breathing. Formal grammar types remain separately blocked.
s=s.replace("'quel rôle joue',",'',1)
p.write_text(s,encoding='utf-8')
print('patched v2 duplicate repairs and semantically aligned residue guard')

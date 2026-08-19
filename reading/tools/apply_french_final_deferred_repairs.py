#!/usr/bin/env python3
"""Apply known qualitative French C2 repairs before the whole-corpus audit."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
C2=R/'reading/french/c2/passages.jsonl'; AUD=R/'reading/audit'; NOTES=AUD/'french_c2_deferred_quality_notes.json'; OUT=AUD/'french_final_deferred_repairs.json'
EXPECTED='c2e64d6d454559931be07d3ec71d5749ec0e063d'
def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def cnt(text,form): return len(re.findall(r'(?<!\w)'+re.escape(form)+r'(?!\w)',text,flags=re.IGNORECASE))
def refresh(row):
 row['word_count']=len(row['text'].split()); row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”\"])?',row['text'])))
 for t in row.get('new_lexical_targets',[]): t['exposures_in_text']=cnt(row['text'],t['form'])
 if not 700<=row['word_count']<=1200 and row.get('cefr')=='C2': raise AssertionError(f"{row['id']} repaired word band {row['word_count']}")
 for t in row.get('new_lexical_targets',[]):
  if t['exposures_in_text']<1: raise AssertionError(f"{row['id']} lost target {t['form']}")
 for t in row.get('review_lexical_targets',[]):
  if cnt(row['text'],t['form'])<1: raise AssertionError(f"{row['id']} lost review form {t['form']}")
def set_role(row,role):
 row['passage_type']=role
 tags=[x for x in row.get('reader_tags',[]) if not x.startswith('unit_role:')]
 row['reader_tags']=['unit_role:'+role]+tags

def repair_u05_p01(r):
 r['genre']='literary prose'
 r['title']='La pièce semblait vide jusqu’à ce que le détail réponde'
 r['text']="""À la fin d’un long trajet, Maëlle arriva devant l’ancien atelier que sa tante lui avait laissé. Le bâtiment se trouvait derrière une gare presque abandonnée, au bout d’une rue où les vitrines s’éteignaient une à une. Elle avait promis de n’y rester qu’une heure. Une entreprise locale lui avait déjà envoyé une offre pour acheter les lieux, et son partenaire l’attendait le lendemain pour signer. Les frais de toiture augmentaient chaque hiver; personne, disait-il, ne pouvait produire un projet raisonnable à partir de murs aussi fatigués. Maëlle avait répété cet argument dans le train jusqu’à le croire simple.

La clé résista, puis la porte céda avec un souffle de poussière. Dans la première salle, les meubles avaient été couverts de draps gris. Un vieux projecteur reposait sous une fenêtre ouverte. Sur le mur du fond, une tache claire dessinait un rectangle presque parfait, comme si quelqu’un avait décroché un tableau quelques minutes plus tôt. Maëlle posa son sac. Une odeur de papier humide, de bois ciré et de métal froid lui revint avec une précision désagréable. Elle se souvenait soudain d’avoir attendu ici, enfant, pendant que sa tante terminait ses commandes.

Elle tira un drap. Des cadres, des plaques d’impression et des boîtes de caractères apparurent. Rien n’avait la beauté tranquille qu’elle avait imaginée dans le train. Tout était rayé, poussiéreux, parfois cassé. Pourtant, le désordre formait un spectacle plus précis que ses souvenirs. Les outils racontaient des gestes : une règle posée de travers, un chiffon durci près d’un flacon vide, une tasse fêlée à côté d’une presse. Maëlle avança sans allumer la lumière, attentive à la façon dont le soir séparait les objets plutôt qu’il ne les cachait.

Au fond de la pièce, elle trouva une enveloppe coincée derrière une planche. Elle portait son prénom. À l’intérieur, aucune lettre, seulement une petite photographie et une bande de papier couverte de chiffres. La photographie montrait la même salle vingt ans plus tôt. Sa tante se tenait près de la fenêtre avec trois apprentis. Derrière eux, une étoile de papier avait été suspendue au plafond pour une fête d’hiver. Maëlle leva les yeux. Le fil qui l’avait tenue était encore là, presque invisible, mais l’étoile avait disparu.

Elle voulut rire de sa propre déception. Un signe manquant ne constituait pas un message. Elle posa la photographie sur la table et examina la bande de chiffres. C’étaient des dates, des quantités, des noms abrégés. Plusieurs correspondaient aux années où l’atelier avait perdu ses gros clients. D’autres semblaient indiquer de petits tirages réalisés gratuitement. À côté d’un nom, sa tante avait écrit : « à reprendre quand ils pourront ». Maëlle reconnut l’association du quartier qui organisait autrefois des cours du soir.

Un bruit monta de la cour. Elle se retourna trop vite et heurta le projecteur. L’appareil glissa de quelques centimètres; un tiroir qu’elle n’avait pas vu s’ouvrit. Il contenait des dizaines de cartes imprimées, toutes différentes. Certaines annonçaient des spectacles scolaires, d’autres des collectes, des mariages, des réunions. Une carte portait une étoile bleue identique à celle de la photographie. Au dos, sa tante avait noté au crayon : « Ils n’avaient pas de quoi payer. On a fait quand même. »

Maëlle resta debout longtemps. Le bâtiment n’était pas devenu rentable par enchantement, et les frais n’avaient pas disparu. L’offre posée dans son téléphone restait raisonnable. Pourtant, la pièce avait changé de forme dans son esprit. Elle n’était plus seulement un bien trop cher à entretenir; elle contenait la trace d’un service rendu, irrégulier et fragile, que les comptes officiels ne racontaient pas entièrement. Cette découverte ne lui dictait pas une décision. Elle ajoutait seulement une question que son calcul initial avait effacée.

La nuit tomba. Dans la vitre, les lampes de la rue se mêlèrent aux objets de l’atelier. Pendant une seconde, Maëlle vit un tableau impossible : la presse ancienne, son propre reflet et, très haut derrière elle, une étoile qui n’existait plus. Elle comprit que le reflet venait d’une enseigne de l’autre côté de la rue. L’explication ne diminua pas l’image. Elle la rendit plus étrange, parce qu’elle montrait combien peu de choses suffisaient à réveiller une mémoire.

Elle remit les cartes dans le tiroir, mais garda la photographie. Avant de partir, elle écrivit à son partenaire : « Ne signe rien demain. J’ai besoin de deux jours. » Puis elle ajouta, après une hésitation : « Je ne sais pas encore ce que je veux sauver. » La phrase lui parut honnête. Elle ferma la porte, respira encore une fois l’odeur de papier humide et descendit vers la gare. Derrière elle, la fenêtre de l’atelier resta noire. Rien ne lui avait donné une réponse; plusieurs détails, pourtant, avaient rendu impossible la réponse trop facile avec laquelle elle était arrivée."""
 ids={t['form']:t['id'] for t in r['new_lexical_targets']}
 qs=[
  ('main_claim','Pourquoi Maëlle reporte-t-elle la signature à la fin du récit ?','Parce que les traces découvertes dans l’atelier ajoutent une valeur historique et relationnelle que son calcul financier initial n’intégrait pas.','spectacle'),
  ('ambiguity_resolution','Pourquoi l’explication du reflet final ne détruit-elle pas son effet ?','Parce que comprendre l’origine matérielle du reflet n’efface pas les associations de mémoire et de perte qu’il déclenche chez Maëlle.','beauté'),
  ('assumption','Quel rôle joue l’étoile absente du plafond ?','Elle relie la photographie, les cartes et le reflet final sans devenir un symbole à signification unique explicitement imposée.','étoile'),
  ('rhetorical_function','Pourquoi le récit reprend-il l’odeur au début et à la fin ?','La reprise encadre le changement de Maëlle et transforme un détail sensoriel en lien entre mémoire, lieu et décision.','odeur'),
  ('stance','Quelle position le récit prend-il sur la décision de conserver l’atelier ?','Il ne tranche pas; il montre plutôt qu’une décision responsable doit intégrer des valeurs que le calcul initial avait laissées hors cadre.','tableau'),
 ]
 for i,(typ,prompt,ans,form) in enumerate(qs,1):
  r['questions'][i-1].update({'type':typ,'prompt':prompt,'target_ids':[ids[form]]}); r['answer_key'][i-1]['answer']=ans
 vocab={
 'spectacle':'Dans le récit, le spectacle est l’ensemble concret des objets et traces qui rend le passé perceptible à Maëlle sans lui fournir une conclusion toute faite.',
 'beauté':'La beauté est présentée comme imparfaite et située : les objets abîmés peuvent néanmoins acquérir une force esthétique par leur relation avec la mémoire et l’usage.',
 'étoile':'L’étoile relie plusieurs moments du récit — photographie, carte et reflet — tout en restant un motif ouvert plutôt qu’un symbole expliqué.',
 'odeur':'L’odeur déclenche la mémoire au seuil de l’atelier puis revient au départ, donnant une continuité sensorielle au changement intérieur de Maëlle.',
 'tableau':'Le tableau désigne l’image composée dans la vitre, où objets, reflet et étoile se superposent pour condenser le conflit entre présent et mémoire.'}
 for j,form in enumerate(['spectacle','beauté','étoile','odeur','tableau'],6): r['answer_key'][j-1]['answer']=vocab[form]

def repair_u06_p04(r):
 r['text']=r['text'].replace('Une note sans date ou un fichier reçu sans contexte peut être authentique tout en étant difficile à relier au résultat final.','Une note sans date ou un reçu sans contexte peut être authentique tout en étant difficile à relier au résultat final.')
 r['text']=r['text'].replace('Un document « reçu » prouve qu’une information a été transmise ou qu’une opération a été enregistrée; il ne prouve pas à lui seul que son contenu a été compris, vérifié ou utilisé dans la décision finale.','Un « reçu » atteste qu’un dépôt, une demande ou une opération a été enregistré à un moment donné; il ne prouve pas à lui seul que le contenu associé a ensuite été compris, vérifié ou utilisé dans la décision finale.')
 for a in r['answer_key']:
  if a['question_id']=='q9': a['answer']='Un « reçu » est ici une preuve d’enregistrement ou de dépôt; il établit une trace de l’opération sans démontrer à lui seul comment l’information associée a été traitée.'

def repair_u10_p03(r):
 r['title']='Perspective complémentaire : mesurer un gain ne suffit pas à autoriser le suivi qui le produit'
 r['text']="""Le second texte reprend le programme de rénovation du dossier précédent. Les économies d’énergie mesurées par le rapport A proviennent en partie de capteurs installés dans les bâtiments pilotes. Ces capteurs enregistrent des données détaillées afin d’identifier les périodes de gaspillage et d’ajuster certains équipements. La perspective complémentaire accepte le résultat technique, mais demande si le même programme peut être jugé uniquement par les économies et les dépenses finales.

Le problème est d’abord formulé comme une question de surveillance. Collecter une information pour régler le chauffage n’équivaut pas nécessairement à suivre les habitudes des habitants, mais la frontière dépend de la précision, de la durée et des possibilités de réutilisation. Autoriser une collecte pour un objectif défini ne signifie donc pas autoriser automatiquement tout usage ultérieur. Une condition de légitimité est que la finalité reste compréhensible et vérifiable. Un participant peut être conscient qu’un capteur existe sans connaître toutes les inférences rendues possibles par l’historique. La priorité devient alors de distinguer l’information nécessaire au réglage de celle qui serait simplement commode pour d’autres analyses.

Le texte répond directement au rapport quantitatif. Un calcul précis des économies peut rester exact tout en laissant ouverte la question des moyens employés. L’objection la plus forte affirme que l’on ne peut pas améliorer le système sans données détaillées. La perspective construit une alternative : conserver localement les mesures les plus fines, transmettre seulement les agrégats nécessaires, puis comparer la performance avec celle du dispositif plus intrusif. Si les économies restent presque identiques, l’avantage supplémentaire de la collecte détaillée devient plus difficile à justifier.

La question technique rejoint ensuite la fiabilité. Une panne peut interrompre les réglages automatiques; brancher plusieurs services au même flux augmente parfois les dépendances. Un système complexe n’est pas nécessairement mauvais, mais chaque connexion ajoute un chemin par lequel une erreur peut se propager. Le dégât potentiel ne se limite pas à une facture plus élevée : une mauvaise configuration peut affecter le confort, l’accès au service ou la confiance des participants. Une performance moyenne élevée n’est donc pas un critère suffisant lorsque certains modes d’échec concentrent leurs conséquences sur un petit groupe.

Une autre objection soutient que les habitants ont accepté le pilote. Le texte distingue accord initial et extension progressive. Si la collecte change de finalité, si sa durée augmente ou si un nouvel acteur reçoit l’accès, la décision n’est plus exactement celle qui avait été présentée. La perspective propose donc une autorisation qui expire, un registre des usages et une procédure simple de contestation. Ces règles ne garantissent pas une absence totale d’erreur; elles rendent cependant les changements visibles et réversibles.

Le lien avec le dossier précédent devient alors plus précis. Le rapport A peut établir une baisse de consommation et le rapport B montrer une distribution budgétaire différente. Le présent texte ajoute une troisième dimension : la manière dont l’information a été obtenue et gouvernée. Ces propositions ne s’annulent pas. Elles répondent à des questions différentes et doivent être rassemblées avant la recommandation. Une politique peut être efficace selon un indicateur, inégale selon un autre et trop intrusive selon un troisième.

La conclusion ne demande pas d’abandonner le programme. Elle recommande un test comparatif entre architectures de collecte, avec des seuils publics de conservation et une voie de retrait. Si une version moins intrusive préserve l’essentiel du bénéfice, elle devient préférable. Si la collecte détaillée produit un gain distinct et important, la décision doit encore exposer qui supporte le risque, quelles protections existent et quelle nouvelle observation ferait modifier l’autorisation. Le désaccord avec le rapport précédent n’est donc pas un refus des chiffres : c’est une demande de compléter ce que les chiffres seuls ne peuvent décider."""
 ids={t['form']:t['id'] for t in r['new_lexical_targets']}
 qa=[
 ('main_claim','Quelle dimension le second texte ajoute-t-il aux deux rapports sur la rénovation ?','Il ajoute la gouvernance de la collecte : finalité, précision, durée, réutilisation, dépendances et possibilité de contestation.','surveillance'),
 ('ambiguity_resolution','Pourquoi accepter un pilote ne revient-il pas à accepter tous les usages futurs des données ?','Parce qu’une nouvelle finalité, une durée plus longue ou un nouvel accès change la décision qui avait été initialement présentée.','autoriser'),
 ('assumption','Que doit montrer le test d’une architecture moins intrusive ?','Il doit comparer si une collecte plus limitée conserve l’essentiel du bénéfice sans exiger les mêmes données détaillées.','condition'),
 ('rhetorical_function','Pourquoi le passage rappelle-t-il qu’un participant peut savoir qu’un capteur existe sans comprendre toutes les inférences ?','Pour distinguer connaissance superficielle du dispositif et compréhension réelle de la portée de la collecte.','conscient'),
 ('stance','Quelle priorité la perspective défend-elle ?','Utiliser l’information nécessaire à la fonction, comparer des solutions moins intrusives et rendre toute extension visible et révisable.','priorité')]
 for i,(typ,prompt,ans,form) in enumerate(qa,1): r['questions'][i-1].update({'type':typ,'prompt':prompt,'target_ids':[ids[form]]}); r['answer_key'][i-1]['answer']=ans
 vocab={
 'surveillance':'La surveillance désigne ici le suivi rendu possible par des données détaillées; son enjeu dépend de la précision, de la durée, des accès et des réutilisations.',
 'autoriser':'Autoriser un usage signifie le permettre dans une finalité et une portée déterminées, sans transformer cette permission en accord illimité.',
 'condition':'Une condition de légitimité est une exigence qui doit rester satisfaite, par exemple une finalité compréhensible, des accès limités et une possibilité de retrait.',
 'conscient':'Être conscient de la présence d’un capteur ne signifie pas nécessairement comprendre toutes les inférences ou réutilisations possibles des données.',
 'priorité':'La priorité consiste à distinguer l’information réellement nécessaire au réglage de celle qui serait seulement utile à des usages supplémentaires.'}
 for j,form in enumerate(['surveillance','autoriser','condition','conscient','priorité'],6): r['answer_key'][j-1]['answer']=vocab[form]


def main():
 before=h(C2)
 if before!=EXPECTED: raise AssertionError(f'Expected sealed U10 blob {EXPECTED}, got {before}; rebase repair plan')
 rows=[json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]
 by={r['id']:r for r in rows}
 set_role(by['fr-c2-u04-p03'],'interleaved'); set_role(by['fr-c2-u04-p04'],'transfer')
 set_role(by['fr-c2-u05-p03'],'interleaved'); set_role(by['fr-c2-u05-p04'],'transfer')
 repair_u05_p01(by['fr-c2-u05-p01']); repair_u06_p04(by['fr-c2-u06-p04']); repair_u10_p03(by['fr-c2-u10-p03'])
 for pid in ['fr-c2-u05-p01','fr-c2-u06-p04','fr-c2-u10-p03']: refresh(by[pid])
 # Preserve the sealed P02/P03 pair id, now made pedagogically coherent by the P03 rewrite.
 if by['fr-c2-u10-p02'].get('paired_text_group')!=by['fr-c2-u10-p03'].get('paired_text_group') or not by['fr-c2-u10-p02'].get('paired_text_group'): raise AssertionError('U10 P02/P03 pair link missing')
 C2.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 after=h(C2)
 report={'status':'PASS','scope':'Known French C2 deferred qualitative repairs','before_c2_blob':before,'after_c2_blob':after,'repairs':[{'issue':'U04 passage role order','passages':['fr-c2-u04-p03','fr-c2-u04-p04'],'action':'P03 interleaved; P04 transfer; reader tags synchronized'},{'issue':'U05 passage role order','passages':['fr-c2-u05-p03','fr-c2-u05-p04'],'action':'P03 interleaved; P04 transfer; reader tags synchronized'},{'issue':'U05 literary-prose genre purity','passages':['fr-c2-u05-p01'],'action':'rewrote as sustained original literary prose; retained five lexical targets and five review forms; refreshed Q/A and exposures'},{'issue':'U06 reçu sense alignment','passages':['fr-c2-u06-p04'],'action':'changed participial received-document usage to noun receipt/proof-of-record sense; updated vocabulary answer'},{'issue':'U10 paired-text coherence','passages':['fr-c2-u10-p02','fr-c2-u10-p03'],'action':'rewrote P03 as a complementary viewpoint on the same renovation/capteur case as P02; preserved pair group and role progression'}],'note':'Per-unit C2 seals before this repair describe the generation frontier and are intentionally superseded for final approval by whole-French post-repair audit artifacts.'}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 notes=json.loads(NOTES.read_text(encoding='utf-8')); notes['status']='APPLIED_PENDING_WHOLE_FRENCH_FINAL_AUDIT'; notes['applied_report']='reading/audit/french_final_deferred_repairs.json'; notes['post_repair_c2_blob']=after; NOTES.write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

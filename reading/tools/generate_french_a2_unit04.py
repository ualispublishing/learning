#!/usr/bin/env python3
# Append French A2 Unit 04 (sequences 19-24) as one guarded batch.
from __future__ import annotations
import json,re,subprocess
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

ROOT=base.ROOT
A1=base.A1
CANON=base.CANON
SCHEMA=base.SCHEMA
EXPECTED_A1_BLOB='0493a2fa13e51b5997db05e91cdea4d8dc5e647b'
EXPECTED_BLOB='488fa3f0638df94624900a155d9f2ed22dbe09a6'
FORMS=('projet','équipe','réunion','responsable','programme','dossier','demande','réponse','service','contact')

def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=s['text']
    return {
        'id':s['id'],'language':'fr','cefr':'A2','unit':4,'sequence':s['sequence'],'revision':1,
        'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],
        'topics':s['topics'],'text':text,'word_count':len(text.split()),
        'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),
        'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,
        'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,
        'speed_training':{
            'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,
            'new_word_policy':'none' if speed else 'controlled',
            'notes':'Generation-stage French A2 Unit 04; final language-wide audit deferred.'
        },
        'quality':{
            'status':'draft','schema_check':'pending','linguistic_review':'pending',
            'pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending',
            'fact_check':'not_required',
            'notes':[
                'Guarded French A2 Unit 04 generation batch.',
                'A1+A2 freshness, exact source identity, A2 word band, review visibility, local target linkage, continuity and zero-new checkpoint are enforced.'
            ]
        },
        'paired_text_group':None,'prerequisites':['French A2 Units 01-03 canonical corpus'],
        'difficulty_notes_internal':'A2 coordination and practical project work with motives, cause/effect, reference chains and problem solving.',
        'reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_a2_u04']
    }

def specs():
    return [
    {
      'id':'fr-a2-u04-p01','sequence':19,'ptype':'instructional','title':'Un projet à préparer',
      'genre':'school project narrative','domains':['educational','personal'],
      'topics':['project','team','planning'],
      'forms':['projet','équipe'],'reviews':['oublier','clé'],
      'text':'''Le club de sciences prépare un projet pour la journée portes ouvertes de l’école. Camille travaille dans une petite équipe avec Sami et deux autres élèves. Leur projet consiste à montrer comment économiser de l’eau à la maison. Au début de la réunion, Camille cherche la clé du local où se trouve le matériel. Elle l’avait mise dans son sac pour ne pas oublier de la rapporter, mais elle ne la voit plus dans la poche habituelle. Toute l’équipe attend pendant qu’elle regarde calmement dans les autres poches. Elle retrouve finalement la clé entre deux cahiers. Comme ils ont perdu quelques minutes, les élèves décident de répartir les tâches avant de commencer. Sami prépare les images, Camille organise les exemples et les deux autres élèves vérifient la liste du matériel. Cette organisation simple permet à l’équipe d’avancer sans se presser et de comprendre clairement ce que chacun doit faire pour le projet.''',
      'grammar':[{'id':'fr-a2-u04-pour-ne-pas','role':'new','description':'use pour ne pas + infinitive to express prevention'}],
      'discourse':[{'id':'fr-a2-u04-task-allocation','role':'new','description':'follow a small problem, recovery and division of tasks'}],
      'items':[
        ('gist','Que prépare le club de sciences ?','Un projet pour la journée portes ouvertes.',['projet']),
        ('literal_detail','Combien d’élèves travaillent avec Camille dans son équipe ?','Trois élèves : Sami et deux autres.',['équipe']),
        ('sequence','Que fait Camille avant que le travail commence vraiment ?','Elle cherche puis retrouve la clé du local.',['clé']),
        ('cause_effect','Pourquoi les élèves répartissent-ils les tâches ?','Parce qu’ils ont perdu quelques minutes et veulent avancer efficacement.',[]),
        ('vocabulary_in_context','Que signifie « projet » ici ?','Un travail organisé que le groupe doit préparer et présenter.',['projet']),
        ('vocabulary_in_context','Que désigne l’« équipe » ?','Le petit groupe d’élèves qui travaille ensemble.',['équipe']),
        ('reference_resolution','Dans « elle ne la voit plus », que remplace « la » ?','La clé.',['clé']),
        ('inference','Pourquoi chacun reçoit-il une tâche précise ?','Pour que le groupe avance sans confusion ni perte de temps.',['équipe']),
        ('cloze_transfer','Complète : Nous préparons un _____ sur l’environnement.','projet',['projet']),
        ('cloze_transfer','Complète : Notre _____ travaille ensemble après les cours.','équipe',['équipe'])
      ]
    },
    {
      'id':'fr-a2-u04-p02','sequence':20,'ptype':'reinforcement','title':'Une réunion mieux organisée',
      'genre':'club meeting narrative','domains':['educational','public'],
      'topics':['meeting','responsibility','lost notes'],
      'forms':['réunion','responsable'],'reviews':['perdre','retrouver'],
      'text':'''Le lendemain, l’équipe se retrouve pour une réunion dans la bibliothèque. La responsable du club, Mme Laurent, demande à chaque groupe de présenter son avancement. Juste avant de parler, Sami pense avoir perdu la feuille où il avait noté les mesures importantes. Il ouvre son dossier, regarde sous la table et vérifie son sac, sans succès. La responsable lui conseille de ne pas chercher partout en même temps. Elle lui demande de se rappeler le dernier endroit où il a utilisé la feuille. Sami se souvient alors qu’il l’avait posée près de l’imprimante. Il va la chercher et peut la retrouver rapidement. La réunion continue sans grand retard. Après les présentations, Mme Laurent explique qu’une personne responsable ne doit pas tout faire elle-même : son rôle est aussi d’aider le groupe à garder une méthode claire. Sami décide donc de ranger ses notes dans une seule pochette avant la prochaine réunion.''',
      'grammar':[{'id':'fr-a2-u04-se-rappeler-ou','role':'new','description':'use se rappeler + embedded clause to recover prior information'}],
      'discourse':[{'id':'fr-a2-u04-guided-recovery','role':'new','description':'use a remembered last location to solve a lost-item problem'}],
      'items':[
        ('gist','Quel problème Sami rencontre-t-il avant de parler ?','Il ne trouve plus sa feuille de notes.',['perdre']),
        ('literal_detail','Qui dirige la réunion ?','Mme Laurent, la responsable du club.',['réunion','responsable']),
        ('sequence','Quel endroit Sami vérifie-t-il après s’être rappelé où il avait utilisé la feuille ?','L’endroit près de l’imprimante.',[]),
        ('cause_effect','Pourquoi retrouve-t-il la feuille plus vite ?','Parce qu’il cherche à partir du dernier endroit où il se souvient de l’avoir utilisée.',['retrouver']),
        ('vocabulary_in_context','Que signifie « réunion » ?','Un moment organisé où plusieurs personnes se rencontrent pour travailler ou discuter.',['réunion']),
        ('vocabulary_in_context','Que signifie « responsable » ici ?','La personne chargée de diriger et d’aider le club.',['responsable']),
        ('reference_resolution','Dans « son rôle est aussi d’aider », à qui renvoie « son » ?','À la responsable du club.',['responsable']),
        ('inference','Pourquoi Sami choisit-il une seule pochette pour ses notes ?','Pour réduire le risque de les perdre avant une réunion.',['perdre','réunion']),
        ('cloze_transfer','Complète : Nous avons une _____ du club à quinze heures.','réunion',['réunion']),
        ('cloze_transfer','Complète : La personne _____ vérifie que chacun connaît sa tâche.','responsable',['responsable'])
      ]
    },
    {
      'id':'fr-a2-u04-p03','sequence':21,'ptype':'interleaved','title':'Le programme dans le bon dossier',
      'genre':'digital coordination narrative','domains':['educational','personal'],
      'topics':['program','folder','sending information'],
      'forms':['programme','dossier'],'reviews':['recevoir','envoyer'],
      'text':'''Mercredi soir, Camille prépare le programme de la présentation : accueil du public, petite expérience, explication des résultats et questions. Elle place le document dans un dossier partagé afin que toute l’équipe puisse le lire. Sami lui écrit qu’il n’arrive pas à recevoir la dernière version. Camille pense d’abord qu’elle a oublié de l’envoyer, mais son application indique le contraire. Elle ouvre alors le dossier et découvre deux fichiers presque identiques. Le programme le plus récent se trouve dans un ancien sous-dossier que Sami ne consulte jamais. Camille décide de déplacer le bon fichier, puis d’envoyer un court message avec son nom exact. Quelques minutes plus tard, Sami confirme qu’il peut le recevoir et l’ouvrir. Ils suppriment ensuite l’ancienne version pour éviter une nouvelle confusion. Cette petite difficulté leur montre qu’un dossier bien organisé ne sert pas seulement à ranger des documents : il aide aussi plusieurs personnes à travailler sur le même programme sans utiliser des versions différentes.''',
      'grammar':[{'id':'fr-a2-u04-afin-que','role':'new','description':'introduce afin que for a clear purpose relation'}],
      'discourse':[{'id':'fr-a2-u04-version-control','role':'new','description':'track file version, location, correction and confirmation'}],
      'items':[
        ('gist','Quel problème empêche Sami de travailler au début ?','Il ne trouve pas la dernière version du programme.',['programme']),
        ('literal_detail','Où se trouve la version la plus récente ?','Dans un ancien sous-dossier.',['dossier']),
        ('sequence','Que fait Camille après avoir trouvé le bon fichier ?','Elle le déplace puis envoie un message avec son nom exact.',['envoyer']),
        ('cause_effect','Pourquoi Sami ne voyait-il pas la dernière version ?','Parce qu’elle se trouvait dans un sous-dossier qu’il ne consultait pas.',['dossier']),
        ('vocabulary_in_context','Que signifie « programme » ici ?','Le plan ordonné des étapes de la présentation.',['programme']),
        ('vocabulary_in_context','Que désigne un « dossier » dans ce texte ?','Un emplacement numérique où des fichiers sont rangés.',['dossier']),
        ('reference_resolution','Dans « ils suppriment ensuite l’ancienne version », qui sont « ils » ?','Camille et Sami.',[]),
        ('inference','Pourquoi suppriment-ils l’ancienne version ?','Pour éviter que quelqu’un utilise encore le mauvais fichier.',['dossier']),
        ('cloze_transfer','Complète : Le _____ indique l’ordre des activités de la journée.','programme',['programme']),
        ('cloze_transfer','Complète : Range ce document dans le bon _____.','dossier',['dossier'])
      ]
    },
    {
      'id':'fr-a2-u04-p04','sequence':22,'ptype':'transfer','title':'Une demande et une réponse',
      'genre':'practical request narrative','domains':['educational','public'],
      'topics':['request','reply','checking payment'],
      'forms':['demande','réponse'],'reviews':['vérifier','payer'],
      'text':'''Jeudi, l’équipe veut emprunter deux petites tables supplémentaires pour sa présentation. Camille remplit une demande auprès du service qui gère le matériel de l’école. Elle explique la date, l’heure et la salle, puis relit le formulaire pour vérifier qu’aucune information ne manque. Le lendemain matin, elle reçoit une réponse : les tables sont disponibles, mais le service demande un petit dépôt qui sera rendu après l’événement. Avant de payer, Camille montre le message à la responsable du club. Celle-ci vérifie que la demande vient bien du service officiel et que le montant correspond aux règles de l’école. Camille peut alors payer sans inquiétude. Elle garde la réponse dans le dossier du projet, avec la preuve du paiement. Plus tard, Sami lui demande pourquoi elle conserve tous ces documents. Camille explique qu’une demande écrite et sa réponse permettent de retrouver rapidement ce qui a été accepté si une question apparaît le jour de la présentation.''',
      'grammar':[{'id':'fr-a2-u04-avant-de-review','role':'integration','description':'reuse avant de + infinitive in a higher-information practical task'}],
      'discourse':[{'id':'fr-a2-u04-request-response-record','role':'new','description':'connect a formal request, reply, verification and stored record'}],
      'items':[
        ('gist','Pourquoi Camille contacte-t-elle le service du matériel ?','Pour obtenir deux tables supplémentaires.',['demande']),
        ('literal_detail','Quelle condition apparaît dans la réponse ?','Il faut payer un petit dépôt.',['réponse','payer']),
        ('sequence','Que fait Camille avant de payer ?','Elle montre le message à la responsable, qui vérifie son origine et le montant.',['vérifier','payer']),
        ('cause_effect','Pourquoi garde-t-elle la réponse et la preuve du paiement ?','Pour pouvoir retrouver ce qui a été accepté en cas de question.',['réponse']),
        ('vocabulary_in_context','Que signifie « demande » ici ?','Une requête écrite pour obtenir du matériel.',['demande']),
        ('vocabulary_in_context','Que signifie « réponse » ici ?','Le message reçu après la demande, qui indique la décision du service.',['réponse']),
        ('reference_resolution','Dans « celle-ci vérifie », à qui renvoie « celle-ci » ?','À la responsable du club.',[]),
        ('inference','Pourquoi la vérification est-elle utile avant le paiement ?','Elle réduit le risque de payer à partir d’un message incorrect.',['vérifier','payer']),
        ('cloze_transfer','Complète : J’envoie une _____ pour utiliser la salle.','demande',['demande']),
        ('cloze_transfer','Complète : J’attends la _____ avant d’organiser la suite.','réponse',['réponse'])
      ]
    },
    {
      'id':'fr-a2-u04-p05','sequence':23,'ptype':'integration','title':'Le bon service et le bon contact',
      'genre':'practical coordination narrative','domains':['educational','public'],
      'topics':['service','contact','phone number','card'],
      'forms':['service','contact'],'reviews':['numéro','carte'],
      'text':'''La veille de la présentation, Camille remarque qu’une prise électrique du local ne fonctionne plus. Sur la carte du bâtiment, elle voit plusieurs bureaux et ne sait pas quel service appeler. Elle consulte le site de l’école et trouve le service technique. Une page indique un contact pour les problèmes urgents, avec un numéro de téléphone différent de celui de l’accueil général. Camille appelle ce numéro et décrit la salle, la prise et l’heure de l’événement. Le contact lui explique qu’un technicien passera dans l’après-midi. Pour éviter une confusion, Camille note le nom du service et le numéro sur une petite carte qu’elle garde avec les documents du projet. Deux heures plus tard, le technicien arrive et répare la prise. Camille comprend alors qu’avoir le bon contact ne signifie pas seulement connaître une personne : il faut aussi savoir quel service peut réellement résoudre le problème et lui donner des informations précises.''',
      'grammar':[{'id':'fr-a2-u04-ne-pas-savoir-quel','role':'new','description':'use an embedded interrogative after ne pas savoir'}],
      'discourse':[{'id':'fr-a2-u04-route-to-service','role':'new','description':'identify the right service, contact it and provide actionable details'}],
      'items':[
        ('gist','Quel problème Camille doit-elle résoudre ?','Une prise électrique du local ne fonctionne plus.',[]),
        ('literal_detail','Quel service trouve-t-elle ?','Le service technique.',['service']),
        ('sequence','Que fait-elle après avoir trouvé le bon numéro ?','Elle appelle et décrit le problème.',['numéro','contact']),
        ('cause_effect','Pourquoi note-t-elle le nom du service et le numéro ?','Pour éviter une confusion et pouvoir retrouver rapidement les coordonnées.',['service','numéro']),
        ('vocabulary_in_context','Que signifie « service » ici ?','Le département de l’école chargé d’un type de problème.',['service']),
        ('vocabulary_in_context','Que signifie « contact » ici ?','La personne ou le point de communication à joindre pour obtenir de l’aide.',['contact']),
        ('reference_resolution','Dans « le contact lui explique », à qui renvoie « lui » ?','À Camille.',['contact']),
        ('inference','Pourquoi le numéro de l’accueil général n’est-il pas le meilleur choix ?','Parce que le service technique dispose d’un contact direct pour ce type de problème.',['service','contact']),
        ('cloze_transfer','Complète : Pour un problème informatique, appelle le bon _____.','service',['service']),
        ('cloze_transfer','Complète : Marie est mon _____ pour cette activité.','contact',['contact'])
      ]
    }
    ]

def checkpoint():
    return {
      'id':'fr-a2-u04-p06','sequence':24,'ptype':'checkpoint','title':'Coordonner un projet sans confusion',
      'genre':'A2 cumulative project-coordination summary','domains':['educational','public','personal'],
      'topics':['project coordination','documents','communication'],
      'text':'''Pour préparer une activité avec d’autres personnes, Camille suit maintenant une méthode plus claire. Au début d’un projet, elle vérifie que chaque membre de l’équipe connaît sa tâche. Pendant une réunion, la personne responsable note les décisions et rappelle les étapes importantes. Un programme simple aide le groupe à savoir ce qui doit arriver et dans quel ordre. Les fichiers sont rangés dans un dossier commun pour que chacun trouve la bonne version. Quand le groupe a besoin de matériel, Camille envoie une demande et conserve la réponse reçue. Si un problème technique apparaît, elle cherche le service compétent et le bon contact au lieu d’appeler plusieurs personnes au hasard. Cette méthode ne supprime pas tous les problèmes, mais elle rend les erreurs plus faciles à comprendre et à corriger. Camille voit surtout qu’une bonne coordination dépend moins de la mémoire d’une seule personne que d’informations claires, partagées et faciles à retrouver.''',
      'grammar':[{'id':'fr-a2-u04-coordination-review','role':'integration','description':'integrate purpose, time and conditional clauses across a practical summary'}],
      'discourse':[{'id':'fr-a2-u04-cumulative-process','role':'integration','description':'summarize a repeatable project-coordination process'}],
      'items':[
        ('gist','Quelle méthode générale le texte présente-t-il ?','Une méthode simple pour coordonner un projet et réduire la confusion.',[]),
        ('literal_detail','Que fait la personne responsable pendant une réunion ?','Elle note les décisions et rappelle les étapes importantes.',['responsable','réunion']),
        ('sequence','Que fait le groupe quand il a besoin de matériel ?','Il envoie une demande et conserve la réponse.',['demande','réponse']),
        ('cause_effect','Pourquoi les fichiers sont-ils rangés dans un dossier commun ?','Pour que chacun puisse trouver la bonne version.',['dossier']),
        ('vocabulary_in_context','Quel rôle joue le programme ?','Il indique ce qui doit arriver et dans quel ordre.',['programme']),
        ('vocabulary_in_context','Que signifie « contact » dans ce contexte ?','Le point ou la personne à joindre dans le service compétent.',['contact','service']),
        ('reference_resolution','Dans « elle rend les erreurs plus faciles », que désigne « elle » ?','La méthode de coordination.',[]),
        ('inference','Pourquoi cette méthode dépend-elle moins de la mémoire d’une seule personne ?','Parce que les informations sont écrites, partagées et organisées.',['équipe','dossier']),
        ('cloze_transfer','Complète : Notre _____ prépare un _____ commun.','équipe ; projet',['équipe','projet']),
        ('summary','Résume en une phrase ce qui évite le plus de confusion.','Partager des informations claires, les ranger correctement et contacter les bonnes personnes.',['service','contact'])
      ]
    }

def build(rows,a1,D):
    P=base.prior(a1+rows)
    failures=[]
    for f in FORMS:
        if f not in D:failures.append(f'{f}:missing_lexicon')
        if P.get(f):failures.append(f'{f}:already_deliberate')
    if failures:raise AssertionError('Unit04 candidate failures: '+', '.join(failures))
    out=[]
    for s in specs():
        new=[base.nt(f,s['text'],D) for f in s['forms']]
        reviews=[base.rev(f,P) for f in s['reviews']]
        ids={t['form']:t['id'] for t in new+reviews}
        out.append(mk(s,new,reviews,ids))
    s=checkpoint()
    reviews=[base.cur(f,D) for f in FORMS]
    ids={t['form']:t['id'] for t in reviews}
    out.append(mk(s,[],reviews,ids,True))
    return out

def main():
    a1_blob=subprocess.check_output(['git','hash-object',str(A1)],text=True).strip()
    if a1_blob!=EXPECTED_A1_BLOB:raise AssertionError(f'A1 blob drift: {a1_blob} != {EXPECTED_A1_BLOB}')
    blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
    if blob!=EXPECTED_BLOB:raise AssertionError(f'A2 blob drift: {blob} != {EXPECTED_BLOB}')
    a1=[json.loads(x) for x in A1.read_text(encoding='utf-8').splitlines() if x.strip()]
    rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(a1)!=60 or a1[-1]['id']!='fr-a1-u10-p06':raise AssertionError('unexpected A1 bridge state')
    if len(rows)!=18 or [r['sequence'] for r in rows]!=list(range(1,19)) or rows[-1]['id']!='fr-a2-u03-p06':
        raise AssertionError('expected exact A2 frontier through Unit03')
    D=base.deck(); unit=build(rows,a1,D)
    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    if [r['sequence'] for r in unit]!=list(range(19,25)):raise AssertionError('Unit04 sequence failure')
    if len({r['id'] for r in rows+unit})!=24:raise AssertionError('Unit04 ID collision')
    old_ids={t['id'] for r in a1+rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')}
    new_ids=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 140<=r['word_count']<=220:raise AssertionError(f"{r['id']}: word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: assessment count")
        amap={a['question_id']:a['id'] for a in r['answer_key']}
        local={t['id'] for field in ('new_lexical_targets','review_lexical_targets') for t in r.get(field,[]) if isinstance(t,dict)}
        if len(amap)!=10:raise AssertionError(f"{r['id']}: answer mapping count")
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id']:raise AssertionError(f"{r['id']} {q['id']}: linkage")
            if any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: undeclared target")
        for t in r['new_lexical_targets']:
            if t['id'] in old_ids:raise AssertionError(f"{r['id']}: reintroduced {t['id']}")
            s=D.get(t['form'])
            if not s or t['source_rank']!=s['rank'] or t['id']!=base.tid(s['rank']):
                raise AssertionError(f"{r['id']}: source identity {t['form']}")
            if base.cnt(r['text'],t['form'])!=t['exposures_in_text']:
                raise AssertionError(f"{r['id']}: exposure mismatch {t['form']}")
            new_ids.append(t['id'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:
                raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(new_ids)!=10 or len(set(new_ids))!=10:raise AssertionError(f'expected 10 unique new targets, got {len(new_ids)}/{len(set(new_ids))}')
    if unit[-1]['new_lexical_targets']!=[]:raise AssertionError('Unit04 P06 must have zero new targets')
    original=CANON.read_text(encoding='utf-8')
    original += '' if original.endswith('\n') else '\n'
    CANON.write_text(original+''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in unit),encoding='utf-8')
    final=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(final)!=24 or [r['sequence'] for r in final]!=list(range(1,25)):raise AssertionError('post-write continuity failure')
    print(json.dumps({'status':'PASS','unit':4,'appended_passages':6,'french_a2_total':24,
      'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':10,'questions':60,'answers':60,
      'checkpoint_new_targets':0},ensure_ascii=False))

if __name__=='__main__':main()

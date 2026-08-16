#!/usr/bin/env python3
"""Append French A1 Unit 06 (sequences 31-36) as one guarded batch."""
from __future__ import annotations
import csv, json, re, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
LEXICON=ROOT/'french_top1000.csv'
EXPECTED_BLOB='d0cdf431e830928617470b4d2d9d7a6b6e161453'
NEW_FORMS=('beaucoup','peu','trop','déjà','aussi','même','souvent','jamais','maintenant','bientôt')

def parse_lexicon():
    out={}
    with LEXICON.open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            form=(row.get('Front') or '').strip(); back=row.get('Back') or ''
            mr=re.search(r'Rank:\s*(\d+)',back); mm=re.search(r'Meaning:\s*(.+)',back); mp=re.search(r'Part of speech:\s*(.+)',back)
            if form and mr and mm and mp: out[form]={'rank':int(mr.group(1)),'sense':mm.group(1).strip(),'pos':mp.group(1).strip()}
    return out

def tid(rank): return f'fr-rank-{rank:04d}'
def count_form(text,form): return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.I|re.UNICODE))
def qa(items):
    qs=[]; ans=[]
    for i,(typ,prompt,answer,tids) in enumerate(items,1):
        qid=f'q{i}'; aid=f'a{i}'; q={'id':qid,'type':typ,'prompt':prompt,'answer_id':aid}
        if tids: q['target_ids']=tids
        qs.append(q); ans.append({'id':aid,'question_id':qid,'answer':answer,'explanation':''})
    return qs,ans

def prior_index(rows):
    out={}
    for r in rows:
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('form'): out.setdefault(t['form'],[]).append(t)
    return out

def nt(form,text,lex):
    s=lex[form]; c=count_form(text,form)
    if c<1: raise AssertionError(f'{form}: no exact running-text exposure')
    return {'id':tid(s['rank']),'form':form,'lemma':form,'intended_sense':s['sense'],'part_of_speech':s['pos'],
            'register':'contemporary standard','variety':None,'context_strategy':['scenario_resolution'],
            'first_introduced':True,'exposures_in_text':c,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}

def review(form,stage,rep,prior):
    hits=prior.get(form,[])
    if len(hits)!=1: raise AssertionError(f'{form}: expected exactly one prior deliberate introduction, got {len(hits)}')
    return {'id':hits[0]['id'],'form':form,'review_stage':stage,'representation':rep,'expected_exposure_number':None}

def current_review(form,stage,rep,lex):
    s=lex[form]; return {'id':tid(s['rank']),'form':form,'review_stage':stage,'representation':rep,'expected_exposure_number':None}

def mk(pid,seq,ptype,title,genre,domains,topics,text,new,reviews,grammar,discourse,items,speed=False):
    qs,ans=qa(items)
    return {'id':pid,'language':'fr','cefr':'A1','unit':6,'sequence':seq,'revision':1,'title':title,'passage_type':ptype,
            'genre':genre,'domains':domains,'topics':topics,'text':text,'word_count':len(text.split()),
            'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,
            'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':grammar,'discourse_targets':discourse,
            'questions':qs,'answer_key':ans,
            'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A1 Unit 06; full multi-pass audit deferred.'},
            'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French A1 Unit 06 generation batch under the active ten-question contract.','Schema, source identity, word band, local target declaration, linkage, review visibility, continuity, and checkpoint invariants are enforced during generation.']},
            'paired_text_group':None,'prerequisites':['French A1 Units 01-05 canonical corpus'],
            'difficulty_notes_internal':'A1 continuation: quantity, excess, prior completion, addition/sameness, frequency/negation, and near-future time.',
            'reader_tags':['unit_role:'+ptype,'generation_batch','french_a1_u06']}

def build(rows,lex):
    prior=prior_index(rows)
    for f in NEW_FORMS:
        if f not in lex: raise AssertionError(f'{f}: missing from french_top1000.csv')
        if prior.get(f): raise AssertionError(f'{f}: already deliberately introduced')
    out=[]
    text='''Le matin, Camille arrive à la cantine une heure avant une activité de classe. Elle a faim, mais elle ne veut pas prendre beaucoup de nourriture. Elle met peu de pain sur son plateau, puis ajoute un fruit et un verre d’eau. Sami prend beaucoup de céréales et lui demande pourquoi son plateau est si léger. Camille répond qu’elle préfère manger peu avant de travailler. Après le repas, elle regarde l’heure et voit qu’il reste encore vingt minutes. Elle range son plateau, remplit sa bouteille et va tranquillement dans la salle. Elle se sent bien parce qu’elle a mangé assez, sans prendre plus que nécessaire.'''
    a,b=nt('beaucoup',text,lex),nt('peu',text,lex)
    out.append(mk('fr-a1-u06-p01',31,'instructional','Beaucoup ou peu ?','cafeteria quantity narrative',['personal','educational'],['food','quantity','morning'],text,[a,b],[review('heure','R2','running_text',prior),review('matin','R2','running_text',prior)],
      [{'id':'fr-a1-beaucoup-quantity','role':'new','description':'beaucoup for a large quantity'},{'id':'fr-a1-peu-quantity','role':'new','description':'peu for a small quantity'}],[{'id':'fr-a1-quantity-choice','role':'new','description':'compare simple quantities in a familiar choice'}],
      [('gist','Que choisit Camille à la cantine ?','Un repas léger avec peu de pain, un fruit et de l’eau.',[]),('literal_detail','Combien de temps reste-t-il après le repas ?','Vingt minutes.',[]),('vocabulary_in_context','Que signifie « beaucoup » quand Sami prend beaucoup de céréales ?','Une grande quantité.',[a['id']]),('vocabulary_in_context','Que signifie « peu » dans « peu de pain » ?','Une petite quantité.',[b['id']]),('cause_effect','Pourquoi Camille mange-t-elle peu avant l’activité ?','Parce qu’elle préfère un repas léger avant de travailler.',[]),('single_word_definition','Que signifie « beaucoup » ici ?','En grande quantité.',[a['id']]),('grammar_function','Dans « peu de pain », que montre « peu » ?','Une petite quantité de pain.',[b['id']]),('contrast','Pour une grande quantité, lequel convient : « beaucoup » ou « peu » ?','beaucoup',[a['id'],b['id']]),('cloze_transfer','Complète : Il y a _____ de livres sur cette grande étagère.','beaucoup',[a['id']]),('cloze_transfer','Complète : Je mets _____ de sucre dans mon thé.','peu',[b['id']])]))

    text='''Cette semaine, Camille a déjà terminé plusieurs devoirs avant le soir. Mercredi, elle ouvre son agenda et voit encore trois exercices. Elle pense d’abord qu’il y en a trop pour une seule soirée. Puis elle remarque qu’un exercice est déjà presque fini. Elle le termine en dix minutes. Il reste alors deux tâches courtes. Camille décide de faire une petite pause avant de continuer. À la fin du soir, tout est terminé. Elle comprend que le mot « trop » dépend parfois du temps disponible et de la taille des tâches. Comme elle avait déjà commencé le travail plus tôt dans la semaine, la soirée est finalement calme.'''
    a,b=nt('trop',text,lex),nt('déjà',text,lex)
    out.append(mk('fr-a1-u06-p02',32,'reinforcement','Déjà presque fini','homework planning narrative',['personal','educational'],['homework','week','evening'],text,[a,b],[review('soir','R2','running_text',prior),review('semaine','R2','running_text',prior)],
      [{'id':'fr-a1-trop-excess','role':'new','description':'trop for an excessive quantity'},{'id':'fr-a1-deja-prior','role':'new','description':'déjà for something completed or true earlier than the current moment'}],[{'id':'fr-a1-task-reassessment','role':'new','description':'revise a simple judgment after checking task size'}],
      [('gist','Pourquoi Camille pense-t-elle d’abord avoir trop de travail ?','Parce qu’elle voit encore trois exercices pour la soirée.',[]),('literal_detail','Combien de tâches reste-t-il après le premier exercice ?','Deux.',[]),('vocabulary_in_context','Que signifie « trop » dans « trop pour une seule soirée » ?','Plus que ce qui semble raisonnable ou nécessaire.',[a['id']]),('vocabulary_in_context','Que signifie « déjà » dans « déjà presque fini » ?','L’exercice était presque fini avant ce moment.',[b['id']]),('inference','Pourquoi la soirée devient-elle finalement calme ?','Parce qu’une partie du travail était déjà faite et les tâches restantes étaient courtes.',[]),('single_word_definition','Que signifie « déjà » ici ?','Avant le moment présent ou plus tôt que prévu.',[b['id']]),('grammar_function','Quel rôle joue « trop » dans « trop de travail » ?','Il indique une quantité excessive.',[a['id']]),('contrast','Pour dire qu’une action est faite avant maintenant, lequel convient : « déjà » ou « bientôt » ?','déjà',[b['id']]),('cloze_transfer','Complète : Ce sac contient _____ de livres ; il est très lourd.','trop',[a['id']]),('cloze_transfer','Complète : J’ai _____ fini mon exercice.','déjà',[b['id']])]))

    text='''Au club de lecture, Camille choisit un livre et Sami prend aussi un livre. Cette fois, ils choisissent même le même titre sans le savoir. Quand ils s’assoient, Camille voit la couverture de Sami et rit. « Moi aussi, j’ai ce livre ! » dit-elle. Sami regarde les deux exemplaires : c’est bien le même livre, mais les couvertures ne sont pas de la même couleur. Ils décident de lire la même première page, puis de parler de ce qu’ils comprennent. Camille note aussi une chose qu’elle trouve intéressante. À la fin, chacun a une idée différente, même après avoir lu exactement le même passage.'''
    a,b=nt('aussi',text,lex),nt('même',text,lex)
    out.append(mk('fr-a1-u06-p03',33,'interleaved','Le même livre','reading-club comparison',['educational','personal'],['reading','same/different','discussion'],text,[a,b],[review('fois','R2','running_text',prior),review('chose','R2','running_text',prior)],
      [{'id':'fr-a1-aussi-addition','role':'new','description':'aussi for addition: too/also'},{'id':'fr-a1-meme-sameness','role':'new','description':'même for the same item'}],[{'id':'fr-a1-same-text-different-idea','role':'new','description':'notice different reactions to the same simple text'}],
      [('gist','Qu’est-ce qui fait rire Camille ?','Elle découvre que Sami a choisi le même livre.',[]),('literal_detail','Qu’est-ce qui est différent entre les deux exemplaires ?','La couleur des couvertures.',[]),('vocabulary_in_context','Que signifie « aussi » dans « Sami prend aussi un livre » ?','Sami fait également cette action.',[a['id']]),('vocabulary_in_context','Que signifie « même » dans « le même livre » ?','Il s’agit du livre identique, pas d’un autre titre.',[b['id']]),('inference','Pourquoi leurs idées peuvent-elles être différentes ?','Parce que deux personnes peuvent comprendre ou remarquer des choses différentes dans le même texte.',[]),('single_word_definition','Que signifie « aussi » ici ?','Également ; de plus.',[a['id']]),('grammar_function','Quel rôle joue « même » devant « livre » ?','Il indique qu’il s’agit d’un livre identique.',[b['id']]),('contrast','Pour dire « également », lequel convient : « aussi » ou « jamais » ?','aussi',[a['id']]),('cloze_transfer','Complète : Ma sœur vient _____ avec nous.','aussi',[a['id']]),('cloze_transfer','Complète : Nous avons le _____ professeur.','même',[b['id']])]))

    text='''Camille va souvent à la bibliothèque après l’école. Elle trouve presque toujours une place près de la fenêtre. Elle ne parle jamais fort dans la salle de lecture. Un jour, Sami lui pose une question : « Tu viens souvent ici le mercredi ? » Camille répond que oui, presque chaque semaine. Elle explique qu’elle ne vient jamais quand elle a un cours de sport tardif. Aujourd’hui, ils choisissent une place au fond de la salle. Sami pose encore une question sur un livre, puis ils commencent à lire. Camille aime cette routine parce qu’elle sait où travailler et peut rester concentrée sans chercher un nouvel endroit chaque fois.'''
    a,b=nt('souvent',text,lex),nt('jamais',text,lex)
    out.append(mk('fr-a1-u06-p04',34,'transfer','Souvent, mais jamais trop fort','library habit narrative',['educational','public'],['library','frequency','rules'],text,[a,b],[review('place','R2','running_text',prior),review('question','R2','running_text',prior)],
      [{'id':'fr-a1-souvent-frequency','role':'new','description':'souvent for frequent occurrence'},{'id':'fr-a1-ne-jamais','role':'new','description':'ne...jamais for never'}],[{'id':'fr-a1-frequency-habit','role':'new','description':'describe how often a familiar routine happens'}],
      [('gist','Quelle habitude de Camille décrit le texte ?','Elle va régulièrement à la bibliothèque après l’école.',[]),('literal_detail','Où Camille et Sami s’installent-ils aujourd’hui ?','Au fond de la salle.',[]),('vocabulary_in_context','Que signifie « souvent » dans « va souvent à la bibliothèque » ?','Cela arrive fréquemment.',[a['id']]),('vocabulary_in_context','Que signifie « jamais » dans « ne parle jamais fort » ?','À aucun moment.',[b['id']]),('cause_effect','Pourquoi Camille aime-t-elle cette routine ?','Parce qu’elle sait où travailler et peut rester concentrée.',[]),('single_word_definition','Que signifie « souvent » ?','Fréquemment ; de nombreuses fois.',[a['id']]),('grammar_function','Dans « ne vient jamais », quels mots forment la négation ?','« ne » et « jamais ».',[b['id']]),('contrast','Pour dire qu’une chose ne se produit à aucun moment, lequel convient : « jamais » ou « souvent » ?','jamais',[a['id'],b['id']]),('cloze_transfer','Complète : Je vais _____ au parc le samedi.','souvent',[a['id']]),('cloze_transfer','Complète : Je ne bois _____ de café le soir.','jamais',[b['id']])]))

    text='''Camille et son petit frère sont maintenant dans le centre de la ville. Une activité pour enfants commence bientôt sur la grande place. Camille regarde l’affiche : il reste quinze minutes. Son frère demande s’ils doivent attendre ici. « Oui, maintenant nous avons le temps de boire un peu d’eau, et bientôt les portes vont ouvrir », répond Camille. Ils s’assoient près d’un arbre. D’autres enfants arrivent bientôt avec leurs parents. Maintenant la place devient plus animée. Quand l’animatrice ouvre la porte, Camille accompagne son frère à l’intérieur. Elle voit qu’il est content d’être arrivé assez tôt et de ne pas avoir couru.'''
    a,b=nt('maintenant',text,lex),nt('bientôt',text,lex)
    out.append(mk('fr-a1-u06-p05',35,'integration','Bientôt, les portes vont ouvrir','community-event narrative',['public','personal'],['city','children','near future'],text,[a,b],[review('enfant','R2','running_text',prior),review('ville','R2','running_text',prior)],
      [{'id':'fr-a1-maintenant-now','role':'new','description':'maintenant for the current moment'},{'id':'fr-a1-bientot-near-future','role':'new','description':'bientôt for the near future'}],[{'id':'fr-a1-wait-near-future','role':'new','description':'relate the current moment to a near-future event'}],
      [('gist','Qu’attendent Camille et son frère ?','Le début d’une activité pour enfants.',[]),('literal_detail','Combien de minutes reste-t-il ?','Quinze minutes.',[]),('vocabulary_in_context','Que signifie « maintenant » dans le texte ?','Au moment présent.',[a['id']]),('vocabulary_in_context','Que signifie « bientôt » dans « les portes vont ouvrir bientôt » ?','Dans peu de temps.',[b['id']]),('sequence','Que font-ils pendant qu’ils attendent ?','Ils boivent un peu d’eau et s’assoient près d’un arbre.',[]),('single_word_definition','Que signifie « bientôt » ?','Dans peu de temps.',[b['id']]),('grammar_function','Quel rôle joue « maintenant » dans la phrase ?','Il situe l’action au moment présent.',[a['id']]),('contrast','Pour le futur proche, lequel convient : « bientôt » ou « déjà » ?','bientôt',[b['id']]),('cloze_transfer','Complète : Je travaille _____ ; je ne peux pas sortir.','maintenant',[a['id']]),('cloze_transfer','Complète : Le bus arrive _____.','bientôt',[b['id']])]))

    text='''Camille organise maintenant ses journées avec plus de facilité. Le matin, elle mange peu si elle n’a pas très faim, mais elle boit beaucoup d’eau. Le soir, elle vérifie si elle a trop de travail ou si une partie est déjà terminée. À la bibliothèque, Sami vient aussi, et ils lisent parfois le même livre. Camille y va souvent, mais elle ne parle jamais fort. Quand une activité commence bientôt, elle regarde l’heure et décide ce qu’elle peut faire maintenant. Ces petits mots l’aident à parler de quantité, de fréquence et de temps avec précision dans des situations très simples.'''
    reviews=[current_review(f,'R1','summary',lex) for f in NEW_FORMS]
    out.append(mk('fr-a1-u06-p06',36,'checkpoint','Quantité, fréquence et temps','cumulative language-use summary',['personal','educational'],['quantity','frequency','time'],text,[],reviews,
      [{'id':'fr-a1-u06-quantity-review','role':'integration','description':'integrate beaucoup/peu/trop'},{'id':'fr-a1-u06-frequency-time-review','role':'integration','description':'integrate frequency and temporal adverbs'}],[{'id':'fr-a1-u06-cumulative-contrast','role':'integration','description':'distinguish simple quantity, frequency, and time meanings'}],
      [('gist','Quelle est l’idée principale du texte ?','Camille utilise plusieurs mots pour parler plus précisément de quantité, de fréquence et de temps.',[]),('literal_detail','Que boit Camille beaucoup ?','De l’eau.',[]),('vocabulary_in_context','Que signifie « déjà » dans ce résumé ?','Qu’une partie du travail est terminée avant le moment présent.',[tid(lex['déjà']['rank'])]),('vocabulary_in_context','Que signifie « souvent » ici ?','Fréquemment.',[tid(lex['souvent']['rank'])]),('reference_resolution','À quoi renvoie « y » dans « Camille y va souvent » ?','À la bibliothèque.',[]),('single_word_definition','Que signifie « peu » ?','En petite quantité.',[tid(lex['peu']['rank'])]),('grammar_function','Dans « ne parle jamais », quel sens porte « jamais » ?','À aucun moment.',[tid(lex['jamais']['rank'])]),('contrast','Pour le moment présent, lequel convient : « maintenant » ou « bientôt » ?','maintenant',[tid(lex['maintenant']['rank']),tid(lex['bientôt']['rank'])]),('cloze_transfer','Complète : Mon ami vient _____ avec moi.','aussi',[tid(lex['aussi']['rank'])]),('summary','Résume en une phrase ce que Camille sait mieux exprimer.','Elle sait mieux exprimer combien, à quelle fréquence et à quel moment une action se produit.',[])],speed=True))
    return out

def main():
    blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
    if blob!=EXPECTED_BLOB: raise AssertionError(f'canonical blob drift: {blob} != {EXPECTED_BLOB}')
    rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows)!=30 or [r['sequence'] for r in rows]!=list(range(1,31)) or rows[-1]['id']!='fr-a1-u05-p06':
        raise AssertionError('expected exact 30-passage frontier through Unit 05')
    lex=parse_lexicon(); unit=build(rows,lex); validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    if [r['sequence'] for r in unit]!=list(range(31,37)) or len({r['id'] for r in rows+unit})!=36: raise AssertionError('Unit 06 continuity failure')
    old_ids={t['id'] for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for r in unit:
        errs=sorted(validator.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:5]]}")
        if not 90<=r['word_count']<=140: raise AssertionError(f"{r['id']}: word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        amap={a['question_id']:a['id'] for a in r['answer_key']}; declared={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id']: raise AssertionError(f"{r['id']} {q['id']}: linkage")
            if any(x not in declared for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: undeclared target")
        for t in r['new_lexical_targets']:
            if t['id'] in old_ids: raise AssertionError(f"{r['id']}: reintroduced {t['id']}")
            s=lex.get(t['form']);
            if not s or t['source_rank']!=s['rank'] or t['id']!=tid(s['rank']): raise AssertionError(f"{r['id']}: source drift {t}")
            if count_form(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: exposure count drift {t['form']}")
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and count_form(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if sum(len(r['new_lexical_targets']) for r in unit[:5])!=10 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('Unit 06 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','unit':6,'appended_passages':6,'sequences':list(range(31,37)),'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':lex[f]['rank'],'id':tid(lex[f]['rank'])} for f in NEW_FORMS],'checkpoint_new_targets':0,'questions':60,'answers':60},ensure_ascii=False))

if __name__=='__main__': main()

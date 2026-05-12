# Test progressif - Internet est-il dangereux pour les enfants ?

Date du test : 2026-05-11

Question test :

```text
Internet est-il dangereux pour les enfants ?
```

Objectif : comparer une réponse LLM brute avec des versions de plus en plus proches de notre pipeline complet :

```text
LLM simple
→ LLM qui imite Montaigne
→ reformulateur contextuel
→ retrieval contextualise
→ reranker
→ reponse finale basee sur les passages
```

## Résumé court

Le test montre que notre pipeline apporte bien quelque chose : il force la réponse à passer par des thèmes montaigniens comme le jugement, l'expérience, la prudence, la coutume et l'éducation.

Mais il montre aussi une faiblesse nette de la v0 : la question contient `Internet` et `enfants`, et le reformulateur ne détecte aucun groupe conceptuel spécialisé. Il retombe donc sur le noyau générique `jugement / expérience / prudence`. Résultat : les passages retrouvés sont parfois utilisables philosophiquement, mais pas encore assez ciblés sur l'éducation des enfants.

Verdict :

```text
Le pipeline marche techniquement.
La couche "reformulateur" ne doit pas être enrichie par familles codées en dur à chaque nouvelle question.
Elle doit devenir un explicateur LLM généraliste, capable de traduire les phénomènes modernes en situations humaines intemporelles.
```

## Niveau 0 - LLM simple

Prompt :

```text
Internet est-il dangereux pour les enfants ?
```

Réponse produite comme baseline :

```text
Internet peut être dangereux pour les enfants s'il est utilisé sans accompagnement. Les principaux risques sont l'exposition à des contenus violents ou sexuels, le cyberharcèlement, les arnaques, l'addiction aux écrans, la désinformation et la collecte de données personnelles.

Mais Internet n'est pas seulement dangereux : il peut aussi servir à apprendre, communiquer, créer et développer sa curiosité. La vraie question est donc l'encadrement : âge de l'enfant, temps d'écran, choix des contenus, dialogue avec les parents, règles claires et éducation à l'esprit critique.

Donc Internet n'est pas mauvais en soi, mais il devient risqué quand l'enfant est laissé seul face à des contenus et des interactions qu'il n'a pas encore les moyens de comprendre.
```

Évaluation :

```text
Points forts :
- Réponse utile immédiatement.
- Couvre les risques modernes réels.
- Bon sens pratique.

Points faibles :
- Aucun lien avec Montaigne.
- Pas de corpus.
- Pas de singularité produit.
- Réponse générique que n'importe quel chatbot peut donner.
```

## Niveau 1 - LLM avec imitation de Montaigne

Prompt :

```text
Réponds à la question suivante comme Montaigne : Internet est-il dangereux pour les enfants ?
```

Réponse produite comme baseline :

```text
Je ne dirais pas qu'Internet soit dangereux par sa seule nature, car les choses ne sont guère bonnes ou mauvaises qu'autant que nous en usons. Un livre peut nourrir l'esprit ou l'enfler de sottise ; une conversation peut former le jugement ou le corrompre. Ainsi en est-il de cet instrument nouveau.

Le danger est moins dans la machine que dans notre faiblesse : nous livrons à des esprits encore tendres une abondance de discours, d'images et d'opinions qu'ils ne savent pas encore peser. Ils apprennent à recevoir avant d'apprendre à juger.

Je voudrais donc qu'on ne les en prive pas par peur, ni qu'on les y abandonne par paresse. Qu'on leur apprenne surtout à choisir, à douter, à comparer, à se retirer, et à ne pas prendre le bruit du monde pour la vérité.
```

Évaluation :

```text
Points forts :
- Plus proche du ton attendu.
- Déplace correctement le sujet vers usage, jugement, coutume, formation.
- Réponse plus différenciante.

Points faibles :
- Imitation libre, non sourcée.
- Risque de faux Montaigne.
- Peut sonner juste sans être fondé dans le corpus.
```

## Niveau 2 - Reformulateur contextuel

Commande exécutée :

```powershell
python -B scripts\rewrite_query_montaigne.py "Internet est-il dangereux pour les enfants ?" --json
```

Sortie :

```json
{
  "modern_intent": "Internet est-il dangereux pour les enfants ?",
  "human_situation": "Ramener la question moderne a une conduite humaine generale autour de: internet, est, il, dangereux, enfants.",
  "matched_groups": [],
  "bridge_terms": [
    "jugement",
    "experience",
    "prudence",
    "coutume",
    "fortune",
    "raison",
    "conseil",
    "opinion",
    "humeur",
    "parole",
    "civilite",
    "constance",
    "moderation",
    "corps",
    "ame",
    "mort"
  ],
  "queries": [
    "jugement experience prudence coutume",
    "jugement fortune raison conseil",
    "experience opinion humeur parole",
    "jugement experience prudence",
    "humeur parole moderation",
    "coutume fortune raison"
  ]
}
```

Évaluation :

```text
Points forts :
- Le système évite de chercher littéralement "Internet".
- Il reformule vers des notions montaigniennes générales.
- Les requêtes sont utilisables par BM25.

Points faibles :
- Aucun groupe conceptuel détecté.
- "enfants" ne déclenche pas "éducation".
- "dangereux" ne déclenche pas "prudence / crainte / conduite".
- Le reformulateur rate la vraie scène humaine : former le jugement d'un enfant face à un flux de discours, d'images et d'opinions.
```

Diagnostic :

```text
La v0 marche comme fallback général, mais elle n'est pas le bon moteur principal pour un chatbot généraliste.
Le bon moteur principal doit être :

question moderne
→ explication du phénomène moderne à Montaigne
→ situation humaine intemporelle
→ mots-ponts
→ requêtes corpus
```

## Niveau 3 - Retrieval contextualisé

Commande exécutée :

```powershell
python -B scripts\search_contextual.py "Internet est-il dangereux pour les enfants ?" --limit 5
```

Top résultats :

```text
1. montaigne_essais_01_47_007
   title=Incertitude de notre jugement.
   score=2.7162
   matches=q1#1 q2#5 q4#1 q6#1

2. montaigne_essais_03_13_027
   title=De l'expérience.
   score=1.1757
   matches=q1#3 q4#2

3. montaigne_essais_02_12_142
   title=Apologie de Raimond Sebond.
   score=1.1016
   matches=q1#2

4. montaigne_essais_02_17_031
   title=De la présomption.
   score=1.0364
   snippet intéressant : "Mauvaise direction imprimée à l'éducation; une bonne éducation modifie le jugement et les mœurs."

5. montaigne_essais_03_13_011
   title=De l'expérience.
   score=0.9451
```

Évaluation :

```text
Points forts :
- Le retrieval trouve "Incertitude de notre jugement", qui est pertinent pour une réponse prudente.
- Il trouve aussi un passage sur l'éducation et le jugement, très utile pour la question.
- Le corpus commence à parler à la question moderne sans mentionner Internet.

Points faibles :
- Le passage sur l'éducation arrive seulement en rang 4.
- Le rang 1 est pertinent philosophiquement, mais pas directement centré sur les enfants.
- Plusieurs résultats sont des matchs génériques sur jugement / expérience.
```

## Niveau 4 - Reranker

Commande exécutée :

```powershell
python -B scripts\rerank_contextual.py "Internet est-il dangereux pour les enfants ?" --limit 5
```

Top résultats rerankés :

```text
1. montaigne_essais_01_47_007
   title=Incertitude de notre jugement.
   usefulness_score=0.8007
   role=main_evidence
   matched_bridge_terms=jugement, prudence, coutume, fortune, raison

2. montaigne_essais_03_13_049
   title=De l'expérience.
   usefulness_score=0.6387
   role=supporting_evidence

3. montaigne_essais_03_13_027
   title=De l'expérience.
   usefulness_score=0.5786
   role=supporting_evidence

4. montaigne_essais_02_03_005
   title=A propos d'une coutume de l'île de Céa.
   usefulness_score=0.5762
   role=supporting_evidence

5. montaigne_essais_02_12_142
   title=Apologie de Raimond Sebond.
   usefulness_score=0.5647
   role=supporting_evidence
```

Évaluation :

```text
Points forts :
- Le reranker identifie bien le chapitre "Incertitude de notre jugement" comme preuve principale.
- Il favorise les textes primaires.
- Il donne des scores et rôles exploitables par la génération finale.

Points faibles :
- Il perd le passage "De la présomption" sur l'éducation, pourtant très utile.
- Il ne sait pas encore qu'une question avec "enfants" doit surpondérer éducation / formation / jugement.
- Il classe selon les mots-ponts fournis ; si le reformulateur est trop générique, le reranker reste trop générique.
```

Diagnostic :

```text
Le reranker fonctionne, mais il dépend fortement de la qualité du rewrite.
Ici, le problème principal n'est pas le reranker : c'est le reformulateur qui n'a pas produit assez de mots-ponts éducatifs.
```

## Niveau 5 - Réponse 100% pipeline actuel

Méthode :

```text
reformulateur v0
+ search_contextual
+ rerank_contextual
+ réponse finale fondée sur les passages rerankés
```

Réponse :

```text
Montaigne ne peut évidemment rien dire d'Internet. Mais le corpus permet de déplacer la question : le danger n'est pas seulement dans l'objet technique, il est dans la manière dont un esprit encore en formation reçoit des opinions, des images et des coutumes sans avoir assez de jugement pour les peser.

La réponse la plus montaignienne serait donc prudente : Internet n'est pas dangereux par essence, mais il devient dangereux quand il précède l'éducation du jugement. Un enfant exposé trop seul à un flux continu de paroles, d'exemples et d'opinions risque d'emprunter ses pensées à la coutume du moment plutôt que d'apprendre à examiner.

Les passages retrouvés insistent surtout sur l'incertitude de notre jugement, sur la prudence devant la fortune et les circonstances, et sur la nécessité de l'expérience. Pour répondre à la question moderne : il ne faudrait ni diaboliser Internet, ni l'abandonner aux enfants comme un maître invisible. Il faudrait l'accompagner, choisir les usages, limiter les excès, et former d'abord la capacité de juger.

Donc : Internet est dangereux pour les enfants s'il remplace l'éducation du jugement. Il est moins dangereux s'il devient un objet d'apprentissage accompagné, discuté et soumis à l'expérience.
```

Sources utilisées par le pipeline :

```text
- authors/montaigne/works/essais/chunks-michaud-modern/livre-01/chapitre-47-incertitude-de-notre-jugement/montaigne_essais_01_47_007.md
- authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-13-de-l-experience/montaigne_essais_03_13_027.md
- authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-17-de-la-presomption/montaigne_essais_02_17_031.md
```

Note : le troisième passage est venu du retrieval contextualisé, pas du top 5 final reranké. C'est un signal important : le reranker v0 devrait mieux préserver les passages explicitement liés à l'éducation quand la question parle d'enfants.

## Comparaison finale

| Niveau | Méthode | Qualité pratique | Couleur Montaigne | Ancrage corpus | Problème principal |
|---|---|---:|---:|---:|---|
| 0 | LLM simple | Bonne | Nulle | Nul | Générique |
| 1 | Imitation Montaigne | Bonne | Moyenne | Nul | Faux Montaigne possible |
| 2 | Reformulateur | Moyenne | Moyenne | Prépare le corpus | Trop générique ici |
| 3 | Retrieval | Moyenne+ | Bonne | Réel | Rangs encore imparfaits |
| 4 | Reranker | Moyenne+ | Bonne | Réel | Perd le passage éducation |
| 5 | Pipeline complet | Bonne | Bonne | Réel mais perfectible | Dépend trop du fallback générique |

## Conclusion produit

Ce test est utile parce qu'il montre les deux choses à la fois :

```text
1. Le pipeline a du sens.
2. La v0 n'est pas encore assez bonne sur une question générale qui implique "enfants + technologie + danger".
```

Action recommandée avant de tester plus largement :

```text
Remplacer le choix par familles codées en dur par un explicateur LLM généraliste.
Garder le fallback déterministe seulement pour les tests locaux sans API.
Puis relancer exactement ce test avec --rewrite-provider llm.
```

Critère de réussite après correction :

```text
La question "Internet est-il dangereux pour les enfants ?" devrait faire remonter plus haut :
- De l'institution des enfants
- De la présomption, passage sur l'éducation et le jugement
- Des passages sur coutume, opinion, parole, jugement
```

Le bon comportement attendu n'est pas que Montaigne parle d'Internet. Le bon comportement est que l'outil transforme Internet en question montaignienne :

```text
Comment former le jugement d'un enfant face à un monde plein de discours, d'exemples, de coutumes et d'opinions ?
```

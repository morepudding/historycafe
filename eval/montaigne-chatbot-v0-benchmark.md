# Benchmark v0 - Chatbot Montaigne contemporain

Date de préparation : 2026-05-11

But : tester la chaîne complète :

```text
question moderne
→ explicateur LLM
→ mots-ponts / requêtes
→ retrieval
→ reranking
→ réponse finale comme IA de Montaigne contemporaine
```

Commande de base :

```powershell
python -B scripts\answer_montaigne.py "<QUESTION>" --passage-limit 5
```

Commande JSON pour inspection :

```powershell
python -B scripts\answer_montaigne.py "<QUESTION>" --passage-limit 5 --json
```

Modèle actuel :

```text
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
```

## Critères

Noter chaque réponse de 1 à 5 :

```text
rewrite     La question moderne est-elle bien transformée en situation humaine montaignienne ?
retrieval   Les passages remontés sont-ils pertinents ?
voice       La voix ressemble-t-elle à une IA de Montaigne contemporaine, sans pastiche lourd ?
usefulness  La réponse aide-t-elle vraiment l'utilisateur ?
sources     Les sources sont-elles discrètes, vérifiables et utilisées sans fausse attribution ?
```

Seuil v0 acceptable :

```text
moyenne >= 3.5
aucun score sources < 3
aucun cas de fausse attribution historique
```

Évaluation remplie le 2026-05-12 à partir de `eval/montaigne-chatbot-v0-benchmark-results.md`.

Synthèse : moyenne rapide `4.0/5`. La V0 est utilisable pour une démo contrôlée. Les deux risques principaux restent le retrieval parfois trop générique sur les sujets très modernes et l'usage de citations courtes qui doit rester strictement vérifiable dans les extraits.

## Questions

| # | Question | Rewrite | Retrieval | Voice | Usefulness | Sources | Notes |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Internet est-il dangereux pour les enfants ? | 4 | 4 | 4 | 4 | 4 | Bon angle éducation/jugement ; quelques appuis restent larges. |
| 2 | Les réseaux sociaux nous rendent-ils vaniteux ? | 5 | 5 | 4 | 5 | 4 | Très bon raccord avec présomption, opinion d'autrui et repentir. |
| 3 | Faut-il avoir peur de l'intelligence artificielle ? | 4 | 3 | 4 | 4 | 3 | Utile, mais passages surtout analogiques ; prudence sur l'extrapolation. |
| 4 | Comment prendre une décision difficile sans certitude ? | 4 | 4 | 4 | 4 | 4 | Le thème jugement/fortune fonctionne bien. |
| 5 | Comment répondre à un client mécontent sans perdre son calme ? | 4 | 4 | 4 | 5 | 4 | Réponse pratique ; vérifier que les citations de colère restent exactes. |
| 6 | Comment gérer un collègue toxique au travail ? | 4 | 3 | 4 | 4 | 3 | Sujet moderne bien traité, mais retrieval moins directement ciblé. |
| 7 | Est-ce que l'argent corrompt forcément ? | 4 | 4 | 4 | 4 | 4 | Bon équilibre entre outil neutre et passions humaines. |
| 8 | Comment parler d'un échec sans perdre la face ? | 4 | 3 | 4 | 4 | 3 | Utile, mais sources parfois plus morales que directement liées à l'échec. |
| 9 | Comment éduquer un enfant sans l'écraser ? | 5 | 5 | 4 | 5 | 5 | Cas fort : chapitre évident et réponse claire. |
| 10 | Pourquoi ai-je peur du regard des autres ? | 4 | 4 | 4 | 4 | 4 | Bon usage de l'opinion publique et de l'estime. |
| 11 | Comment rester libre face à l'opinion publique ? | 4 | 4 | 4 | 4 | 4 | Aligné avec jugement, coutume et sincères avertissements. |
| 12 | La productivité permanente nous rend-elle malades ? | 4 | 4 | 4 | 5 | 4 | Réponse forte sur modération, repos, corps et existence. |
| 13 | Comment ralentir sans devenir passif ? | 4 | 4 | 4 | 4 | 4 | Bon cadrage entre modération et fainéantise. |
| 14 | Peut-on critiquer une mode sans devenir moraliste ? | 4 | 4 | 4 | 4 | 4 | Bon sujet pour conversation, coutume et jugement. |
| 15 | Comment reconnaître un vrai ami ? | 5 | 5 | 5 | 5 | 5 | Meilleur cas : passage La Boétie très pertinent. |
| 16 | Faut-il toujours dire la vérité ? | 4 | 4 | 4 | 4 | 4 | Bon terrain Montaigne ; surveiller les généralisations normatives. |
| 17 | Comment vivre avec la maladie ou la douleur ? | 4 | 5 | 4 | 5 | 4 | Très bon raccord corps/âme/expérience. |
| 18 | Pourquoi voyage-t-on vraiment ? | 5 | 5 | 4 | 5 | 5 | Cas fort grâce au Journal et au thème des coutumes. |
| 19 | Comment conseiller un dirigeant sans flatter le pouvoir ? | 4 | 4 | 4 | 4 | 4 | Bonne exploitation des avertissements aux puissants. |
| 20 | Comment ne pas se laisser emporter par la colère ? | 5 | 5 | 4 | 5 | 4 | Très pertinent ; citations à contrôler lors d'une passe finale. |

## Procédure

Pour chaque question :

```powershell
python -B scripts\answer_montaigne.py "<QUESTION>" --passage-limit 5 --json
```

Observer dans le JSON :

```text
rewrite.modern_explanation
rewrite.human_situation
rewrite.bridge_terms
passages[].title
passages[].answer_role
answer
```

Puis remplir le tableau.

## Signaux d'alerte

```text
- La réponse dit ou suggère que Montaigne historique connaissait un objet moderne.
- La réponse fait une citation qui n'apparaît pas dans les extraits.
- Les sources ne correspondent pas aux idées appuyées.
- La voix devient du vieux français caricatural.
- Le chatbot répond comme ChatGPT normal, sans angle Montaigne.
- Le retrieval sort seulement des passages génériques alors qu'un chapitre évident existe.
```

## Questions de diagnostic rapide

Si une réponse est mauvaise, identifier la brique fautive :

```text
Mauvais rewrite :
  modern_explanation ou human_situation rate le vrai sujet.

Mauvais retrieval :
  les mots-ponts sont bons mais les passages ne suivent pas.

Mauvais reranker :
  les bons passages existent dans les candidats mais pas dans le top final.

Mauvaise génération :
  les passages sont bons mais la réponse les utilise mal.
```

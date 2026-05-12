# Benchmark OpenRouter Nemotron - echantillon Montaigne

## Setup

Modele :

```text
nvidia/llama-nemotron-embed-vl-1b-v2:free
```

Provider :

```text
OpenRouter
```

Echantillon :

```text
121 chunks
2048 dimensions
```

Composition :

- Essais cibles : amitie, moderation, colere, conversation, experience.
- Journal de voyage : 12 chunks.
- Correspondance complete : 64 chunks.
- Biographies/critiques : 8 chunks.

## Resultats rapides

Le modele donne de bons signaux sur les requetes conceptuelles :

- `repondre a un client mecontent avec tact et fermete` remonte surtout `De la colere` et `De la conversation`.
- `critiquer une mode actuelle sans faire le moraliste` remonte `De la conversation` et `De la moderation`.
- `prendre une decision difficile sans certitude artificielle` remonte `De l'experience`.
- `amitie La Boetie` remonte `De l'amitie` et la lettre sur La Boetie.
- `voyage observation coutumes` remonte bien le Journal de voyage.

## Limites observees

Sur des requetes avec noms propres explicites, la recherche vectorielle peut generaliser trop fortement.

Exemple :

```text
Mademoiselle de Montaigne femme consolation Plutarque
```

BM25 retrouve directement la lettre a sa femme. Le vectoriel remonte d'abord la lettre sur La Boetie, probablement parce que le champ semantique `femme / maladie / mort / consolation` est proche.

Conclusion : il faut garder une recherche hybride, avec un leger poids supplementaire pour BM25.

## Decision

Le modele OpenRouter/Nemotron est suffisant pour lancer un index complet V0.

Il ne doit pas remplacer BM25. Le bon usage est :

```text
BM25 pour noms propres, titres, citations, correspondances exactes.
Vectoriel pour requetes modernes et rapprochements semantiques.
Hybrid pour le chatbot.
```


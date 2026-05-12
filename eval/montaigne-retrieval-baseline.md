# Baseline retrieval Montaigne

## Etat

Le corpus est indexe dans :

```text
authors/montaigne/indexes/corpus-index.jsonl
```

Le moteur de recherche actuel est volontairement simple :

```text
scripts/search_corpus.py
```

Il utilise BM25 lexical, sans embeddings.

Un pipeline vectoriel existe aussi :

```text
scripts/embed_corpus.py
scripts/search_vector.py
scripts/search_hybrid.py
```

Le provider `local-hash` est disponible sans dependances externes, mais il sert surtout a valider les fichiers et la mecanique vectorielle. Pour tester la vraie recherche semantique, utiliser le provider `openai` avec une cle API.

## Ce que ce baseline valide

- Les chunks sont lisibles et charges depuis un manifest unique.
- Les sources sont preservees.
- Les textes primaires recoivent un poids plus fort que les biographies.
- Les retraductions IA restent marquees comme non citables directement.
- Les notes editoriales sont degradees dans le ranking.

## Ce que ce baseline ne valide pas

- La comprehension semantique de requetes modernes, tant que les vrais embeddings ne sont pas generes.
- La reformulation de questions contemporaines vers des passages anciens.
- La selection fine de passages quand les mots de la question ne sont pas dans le corpus.

## Resultat attendu

Pour des requetes proches du corpus, le baseline doit sortir de bons passages.

Pour des requetes modernes, il peut echouer ou sortir des passages trop litteraux. Ce n'est pas un probleme du corpus : c'est le signal qu'il faudra brancher un vrai retrieval vectoriel.

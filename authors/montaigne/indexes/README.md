# Index Montaigne

Ce dossier contient les artefacts generes pour tester le retrieval du corpus Montaigne.

## Fichiers

- `corpus-index.jsonl` : un enregistrement JSON par chunk.
- `corpus-stats.json` : statistiques globales de l'index.

## Regeneration

```powershell
python scripts\build_corpus_index.py
```

## Recherche locale

```powershell
python scripts\search_corpus.py "amitie la boetie" --limit 8
python scripts\search_corpus.py "pouvoir politique conseiller le roi avec prudence" --limit 8
python scripts\search_corpus.py "experience corps maladie voyage observation" --limit 8
```

## Reformulation contextuelle

Pour les questions modernes, passer d'abord par le reformulateur corpus :

```powershell
python scripts\rewrite_query_montaigne.py "comment gerer un collegue toxique au travail" --json
```

Le mode par defaut est un fallback local deterministe. Pour le mode generaliste, utiliser le reformulateur LLM :

```powershell
python scripts\rewrite_query_montaigne.py "internet est-il dangereux pour les enfants" --provider llm --json
```

Puis tester directement la recherche BM25 multi-requetes :

```powershell
python scripts\search_contextual.py "aide-moi a repondre a un client mecontent avec fermete et respect" --limit 8
```

Pour garder les passages les plus utiles a la reponse, utiliser le reranker v0 :

```powershell
python scripts\rerank_contextual.py "aide-moi a repondre a un client mecontent avec fermete et respect" --limit 5
```

Avec une cle `OPENAI_API_KEY` ou `OPENROUTER_API_KEY`, la recherche complete peut utiliser l'explicateur LLM :

```powershell
python scripts\rerank_contextual.py "internet est-il dangereux pour les enfants" --rewrite-provider llm --limit 5
```

## Reponse finale

Le generateur final repond comme une IA de Montaigne contemporaine : elle connait les objets modernes, sait qu'elle est une IA inspiree de Montaigne, et s'appuie sur les passages retrouves.

```powershell
python scripts\answer_montaigne.py "internet est-il dangereux pour les enfants"
```

Benchmark v0 :

```text
eval/montaigne-chatbot-v0-benchmark.md
```

Cette v0 ne fait pas une traduction litteraire vers le XVIe siecle. Elle explique d'abord le phenomene moderne en situation humaine intemporelle, puis genere des mots-ponts et requetes courtes compatibles avec le corpus.

## Recherche vectorielle

Generation locale sans API :

```powershell
python scripts\embed_corpus.py --provider local-hash --dimensions 768
```

Recherche vectorielle locale :

```powershell
python scripts\search_vector.py "Mademoiselle de Montaigne ma femme consolation Plutarque" --limit 8
```

Recherche hybride BM25 + vectoriel :

```powershell
python scripts\search_hybrid.py "Mademoiselle de Montaigne ma femme consolation Plutarque" --limit 8
```

Generation avec embeddings OpenAI, si `OPENAI_API_KEY` est defini :

```powershell
python scripts\embed_corpus.py --provider openai --model text-embedding-3-small --dimensions 1536 --out-npz authors\montaigne\indexes\corpus-embeddings-openai.npz --out-meta authors\montaigne\indexes\corpus-embeddings-openai.json
```

Puis :

```powershell
python scripts\search_vector.py "repondre a un client mecontent avec tact" --vectors authors\montaigne\indexes\corpus-embeddings-openai.npz --meta authors\montaigne\indexes\corpus-embeddings-openai.json
```

Generation avec OpenRouter, si `OPENROUTER_API_KEY` ou `OPEN_ROUTER_API_KEY` est defini :

```powershell
python scripts\embed_corpus.py --provider openrouter --model nvidia/llama-nemotron-embed-vl-1b-v2:free --batch-size 16 --out-npz authors\montaigne\indexes\corpus-embeddings-openrouter-nemotron.npz --out-meta authors\montaigne\indexes\corpus-embeddings-openrouter-nemotron.json
```

Puis :

```powershell
python scripts\search_hybrid.py "repondre a un client mecontent avec tact" --vectors authors\montaigne\indexes\corpus-embeddings-openrouter-nemotron.npz --meta authors\montaigne\indexes\corpus-embeddings-openrouter-nemotron.json
```

## Limite importante

Le moteur `search_corpus.py` est un baseline lexical BM25.

Le mode `local-hash` est seulement un baseline vectoriel local. Il valide le pipeline sans dependance externe, mais il ne remplace pas un vrai modele d'embeddings semantiques.

Pour des questions modernes ou indirectes, par exemple "repondre a un client mecontent", il faudra utiliser les embeddings OpenAI ou un modele local multilingue de type sentence-transformers.

# Traduction francaise de travail des lettres anglaises

## Objectif

Creer une couche francaise lisible des 16 lettres importees depuis Wikisource EN.

Cette couche servira a enrichir le chatbot en francais, mais elle devra rester clairement marquee comme une retraduction de travail depuis une traduction anglaise du XIXe siecle.

## Dossiers

Source anglaise valide :

```text
chunks-en/
```

Future traduction francaise de travail :

```text
chunks-fr-ai-draft/
```

## Metadonnees obligatoires pour chaque chunk traduit

```yaml
language: fr
original_language: fr
translated_from_language: en
translation_status: ai_draft
source_quality: useful_but_not_original
use_for_voice: true
use_for_exact_french_style: false
use_for_direct_quote: false
```

## Regle d'usage IA

Les lettres retraduites peuvent servir a comprendre :

- les relations personnelles de Montaigne ;
- son ton face au deuil ;
- son rapport a son pere, a sa femme, a La Boetie ;
- son role public a Bordeaux ;
- son rapport au pouvoir royal.

Elles ne doivent pas servir a produire des citations francaises presentees comme authentiques.

Si le chatbot cite une lettre retraduite, il doit signaler que la formulation francaise est une traduction de travail.

## Lettres prioritaires pour traduction

1. Lettre I : mort de La Boetie, deja disponible en francais original dans `chunks/lettre-mort-la-boetie/`.
2. Lettre VII : a sa femme, tres importante pour le ton intime.
3. Lettres XIV-XV : a Henri IV, importantes pour le rapport au pouvoir.
4. Lettres IX-XI : jurats de Bordeaux, importantes pour le Montaigne maire.
5. Lettre II : dedicace a son pere pour Sebond.

## Strategie

Traduire par petits lots, lettre par lettre, et relire au minimum les lettres VII, XIV et XV.

Ne pas chercher un faux style XVIe siecle. Le but est une version francaise claire, contemporaine, utilisable par le RAG.


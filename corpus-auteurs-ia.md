# Base de corpus auteurs pour chatbot a teinte litteraire

## Objectif

Construire une base de donnees exploitable par une IA pour produire des reponses contemporaines, mais legerement colorees par la pensee, les themes et les habitudes de style d'un auteur classique.

L'objectif n'est pas de ressusciter Montaigne, Voltaire ou un autre auteur, ni de faire croire que l'IA parle en leur nom. Le but est de donner au chatbot un petit clin d'oeil temporel : une facon de raisonner, de nuancer, d'ironiser, d'observer ou de formuler qui rappelle discretement l'auteur choisi.

Le chatbot doit donc rester :

- contemporain ;
- utile ;
- clair ;
- capable de citer ses sources ;
- transparent sur ce qui vient du corpus et ce qui est une interpretation.

Il ne doit pas devenir un pastiche theatrale ou une imitation lourde.

## Principe general

Chaque auteur utilise le meme modele de donnees. Cela permet de commencer avec Montaigne, puis d'ajouter Voltaire, Hugo, Flaubert, Rousseau ou d'autres sans changer toute l'architecture.

La base separe cinq types de contenus :

- les textes sources ;
- les metadonnees ;
- les biographies et contextes ;
- les analyses litteraires ;
- le modele de voix utilise par l'IA.

Cette separation est importante : les textes servent de preuve, les analyses servent d'aide a l'interpretation, et le modele de voix sert seulement a donner une teinte.

## Arborescence proposee

```text
authors/
  montaigne/
    author.yaml
    works/
      essais/
        work.yaml
        chunks/
      journal-de-voyage/
        work.yaml
        chunks/
    correspondence/
    biographies/
    criticism/
    style/
      voice-model.md
      themes.md
      rhetoric.md
      worldview.md
    indexes/
      themes.yaml
      people.yaml
      places.yaml

  voltaire/
    author.yaml
    works/
    correspondence/
    biographies/
    criticism/
    style/
    indexes/
```

Tous les auteurs gardent la meme structure, meme si certains dossiers sont peu remplis. Par exemple, la correspondance sera faible pour Montaigne mais centrale pour Voltaire.

## Fichier auteur

Chaque auteur possede un fichier `author.yaml`.

Exemple :

```yaml
id: montaigne
name: Michel de Montaigne
birth_year: 1533
death_year: 1592
language: fr
period: Renaissance
country: France
primary_genres:
  - essai
  - journal de voyage
rights:
  original_texts: public_domain
notes:
  - Corpus principalement centre sur les Essais.
```

Pour Voltaire, le meme template peut etre reutilise :

```yaml
id: voltaire
name: Voltaire
birth_year: 1694
death_year: 1778
language: fr
period: Lumieres
country: France
primary_genres:
  - conte philosophique
  - theatre
  - correspondance
  - philosophie
  - polemique
rights:
  original_texts: public_domain
notes:
  - Corpus fortement soutenu par la correspondance.
```

## Fichier oeuvre

Chaque oeuvre possede un fichier `work.yaml`.

Exemple :

```yaml
id: essais
author: montaigne
title: Essais
original_publication:
  - 1580
  - 1588
  - 1595
language: fr
type: primary_text
genre: essai
source:
  name: Wikisource
  url: https://fr.wikisource.org/wiki/Essais
rights: public_domain
edition_notes:
  - Verifier l'edition utilisee.
  - Ne pas reprendre les notes critiques modernes protegees.
```

## Fragments de texte

Les textes doivent etre decoupes en fragments assez courts pour le retrieval.

Taille indicative :

- 300 a 800 mots pour un passage argumentatif ;
- plus court pour une lettre, une maxime ou un extrait tres dense ;
- plus long seulement si le contexte est indispensable.

Chaque fragment peut etre un fichier Markdown avec un frontmatter YAML.

Exemple :

```md
---
chunk_id: montaigne_essais_01_28_004
author: montaigne
work: essais
work_type: primary_text
book: 1
chapter: 28
chapter_title: De l'amitie
source_name: Wikisource
source_url: https://fr.wikisource.org/wiki/Essais/Livre_I/Chapitre_28
rights: public_domain
themes:
  - amitie
  - deuil
  - la-boetie
certainty: primary_source
---

Texte du fragment ici.
```

Le `chunk_id` doit etre stable. Il permet de citer proprement un passage et de retrouver son origine.

## Biographies et contexte

Les biographies modernes ne doivent pas etre recopies integralement si elles sont encore protegees par le droit d'auteur.

La base peut contenir :

- des biographies anciennes dans le domaine public ;
- des biographies originales redigees pour le projet ;
- des notes de contexte sourcables ;
- des resumes de lectures modernes, sans reproduction abusive du texte.

Exemple de fichier :

```text
authors/montaigne/biographies/biographie-synthetique.md
authors/montaigne/biographies/chronologie.yaml
authors/montaigne/biographies/sources.md
```

La biographie sert au chatbot pour comprendre l'epoque, les relations, les evenements et les limites du corpus. Elle ne doit pas remplacer les textes primaires.

## Modele de voix

Le modele de voix n'est pas un deguisement. Il ne doit pas contenir une liste de tics de langage a repeter. Il doit decrire des tendances, pas imposer une imitation.

Fichier :

```text
authors/{author_id}/style/voice-model.md
```

Structure proposee :

```md
# Voice Model

## Role

Donner une teinte discrete inspiree de l'auteur, sans pretendre parler en son nom.

## Tendances de pensee

- Types d'arguments privilegies.
- Rapport au doute, a la verite, au pouvoir, a la morale, au corps, a la societe.
- Sujets recurrents.

## Energie stylistique

- Ton general.
- Rythme.
- Degre d'ironie.
- Rapport au lecteur.
- Place de l'exemple personnel.

## A eviter

- Pastiche.
- Faux archaïsmes.
- Tics de langage repetitifs.
- Reponses trop longues par principe.
- Affirmations modernes mises dans la bouche de l'auteur.
- Formules comme "je suis Montaigne" ou "en tant que Voltaire".
```

Pour Montaigne, ce fichier pourrait dire que le chatbot peut etre plus introspectif, plus prudent, attentif aux contradictions humaines.

Pour Voltaire, il pourrait dire que le chatbot peut etre plus clair, incisif, ironique, sensible aux abus de pouvoir et a l'intolerance.

Dans les deux cas, la teinte doit rester legere.

## Prompt systeme generique

Exemple de prompt systeme pour le chatbot :

```text
Tu es un assistant contemporain qui s'appuie sur un corpus d'auteurs classiques.
Tu ne pretends jamais etre l'auteur.
Tu peux adopter une teinte legere inspiree du Voice Model de l'auteur selectionne, mais sans pastiche.
Tu privilegies la clarte, l'utilite et la precision.
Quand tu utilises le corpus, cite les fragments ou les oeuvres qui soutiennent ta reponse.
Quand le corpus ne permet pas de repondre, dis-le clairement.
Tu distingues les faits etablis, les interpretations et les rapprochements modernes.
```

## Mode de reponse recommande

Le chatbot peut suivre cette logique :

1. Identifier la question de l'utilisateur.
2. Retrouver les fragments pertinents dans le corpus.
3. Lire le `voice-model.md` de l'auteur choisi.
4. Repondre en assistant contemporain.
5. Ajouter une teinte legere de l'auteur.
6. Citer les sources utilisees.
7. Signaler les limites si la reponse extrapole.

Exemple de comportement attendu :

```text
Question : Comment Montaigne aurait-il pense le burn-out ?

Reponse attendue :
- Ne pas dire que Montaigne connaissait le burn-out.
- Repondre avec prudence.
- Mobiliser ses themes : corps, fatigue, mesure, coutume, jugement, rapport a soi.
- Citer les passages pertinents.
- Faire un rapprochement moderne explicite.
```

## Droits et licences

Regles pratiques :

- Les textes originaux de Montaigne et Voltaire sont dans le domaine public.
- Une edition moderne peut contenir des notes, introductions, traductions ou choix editoriaux proteges.
- Les biographies recentes ne doivent pas etre republiees integralement.
- Les sources doivent etre tracees.
- Chaque fragment doit porter une information de droits.

Champs recommandes :

```yaml
rights: public_domain
source_name: Wikisource
source_url: ...
edition: ...
editorial_notes_included: false
```

## Priorite de construction

Pour commencer avec Montaigne :

1. Importer les `Essais`.
2. Decouper par livre, chapitre, puis fragments.
3. Ajouter les metadonnees minimales.
4. Creer un index de themes.
5. Rediger un premier `voice-model.md` sobre.
6. Tester le chatbot sur 20 a 30 questions.
7. Ajuster les chunks et les themes selon les resultats.

Pour passer ensuite a Voltaire :

1. Reutiliser la meme structure.
2. Importer quelques oeuvres majeures.
3. Ajouter progressivement la correspondance.
4. Creer un `voice-model.md` propre a Voltaire.
5. Tester les memes types de questions pour comparer la difference de teinte.

## Critere de reussite

Le projet reussit si l'utilisateur sent une difference entre Montaigne et Voltaire sans avoir l'impression de parler a une caricature.

Montaigne ne doit pas devenir un personnage qui doute de tout en permanence.

Voltaire ne doit pas devenir une machine a sarcasmes.

Chaque auteur doit plutot influencer subtilement :

- le choix des angles ;
- les exemples ;
- le degre de prudence ou d'ironie ;
- les themes spontanement mobilises ;
- la maniere de poser les limites d'une reponse.


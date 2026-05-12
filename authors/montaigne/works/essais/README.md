# Essais - import initial

Ce dossier contient le premier import exploitable des *Essais* de Montaigne pour le projet HistoryCafe.

## Source

Source utilisee : Project Gutenberg, *Essais de Montaigne (self-edition)*, edition Michaud, 1909.

Fichier source principal :

- `sources/gutenberg-michaud.yaml`

Fichiers bruts telecharges :

- `raw/gutenberg-48529.txt`
- `raw/gutenberg-49168.txt`
- `raw/gutenberg-58801.txt`
- `raw/gutenberg-58706.txt`

## Couche textuelle

Le premier import utilise la traduction en francais moderne de l'edition Michaud, pas le texte ancien.

Raison : cette couche est plus directement exploitable par un chatbot RAG. Le texte ancien pourra etre ajoute plus tard comme autre `text_layer`, sans changer le modele de donnees.

## Dossier de chunks valide

Le dossier valide est :

```text
chunks-michaud-modern/
```

Le dossier `chunks/` peut contenir une generation de test incomplete et doit etre ignore.

## Resultat du decoupage

Generation actuelle :

- Livre I : 57 chapitres
- Livre II : 37 chapitres
- Livre III : 13 chapitres
- Total : 107 chapitres
- Total : 1124 chunks Markdown

Chaque chunk contient un frontmatter avec :

- `chunk_id`
- `author_id`
- `work_id`
- `source_id`
- `source_url`
- `book`
- `chapter`
- `chapter_title`
- `chunk_index`
- `word_count`
- `text_layer`
- `rights`

## Regeneration

Pour regenerer les chunks :

```powershell
python scripts\chunk_montaigne_essais.py
```

Le script lit les fichiers dans `raw/`, isole la traduction moderne, detecte livres et chapitres, puis decoupe les chapitres en fragments de taille adaptee au retrieval.


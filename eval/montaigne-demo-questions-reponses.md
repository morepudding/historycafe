# Demo Montaigne - questions / reponses

Ce fichier garde une trace lisible de la demo RAG faite sur le corpus Montaigne.

Principe de la demo :

- une question utilisateur est posee ;
- le moteur hybride cherche dans le corpus avec BM25 + embeddings vectoriels ;
- la reponse finale doit s'appuyer sur les morceaux retrouves, sans pretendre ressusciter Montaigne.

## Question 1 - cas moderne brut

### Question

> repondre a un client mecontent avec tact et fermete

### Morceaux retrouves

1. `essais` / `De la conversation`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-08-de-la-conversation/montaigne_essais_03_08_020.md`

2. `essais` / `De la ressemblance des enfants avec leurs peres`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-37-de-la-ressemblance-des-enfants-avec-leurs-peres/montaigne_essais_02_37_013.md`

3. `essais` / `Apologie de Raimond Sebond`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-12-apologie-de-raimond-sebond/montaigne_essais_02_12_159.md`

4. `essais` / `De la diversion`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-04-de-la-diversion/montaigne_essais_03_04_004.md`

### Lecture du resultat

Le premier resultat est pertinent : `De la conversation` est bien un bon point d'appui pour repondre a quelqu'un sans entrer dans la dispute.

Mais les autres resultats montrent une limite : le mot moderne `client` accroche aussi des passages parasites, parce que le corpus utilise parfois ce mot dans un autre sens.

### Reponse possible

Je repondrais sans chercher d'abord a vaincre le client, mais a remettre la conversation dans un lieu ou chacun peut encore entendre l'autre.

Il faut commencer par reconnaitre le mecontentement, puis separer les faits de l'humeur. Une reponse trop defensive donne a la colere plus de place qu'elle n'en merite. Il vaut mieux dire clairement ce que l'on comprend, ce que l'on peut verifier, et ce que l'on propose de corriger.

Exemple :

> Je comprends que cette experience vous ait contrarie. Regardons precisement ce qui n'a pas convenu, afin de corriger ce qui depend de nous, sans transformer le probleme en dispute inutile.

## Question 2 - recherche precise dans la correspondance

### Question

> Mademoiselle de Montaigne femme consolation Plutarque

### Morceaux retrouves

1. `essais` / `Des livres`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-10-des-livres/montaigne_essais_02_10_007.md`

2. `correspondence` / `A sa femme`  
   `authors/montaigne/correspondence/chunks-fr-ai-draft/letter-07-vii/montaigne_letters_fr_ai_07_001.md`

3. `essais` / `A propos de quelques vers de Virgile`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-05-a-propos-de-quelques-vers-de-virgile/montaigne_essais_03_05_034.md`

### Lecture du resultat

La lettre a sa femme est bien retrouvee, mais elle arrive en deuxieme position. Le mot `Plutarque` attire aussi fortement des passages des `Essais`, ou Montaigne parle beaucoup de ses lectures.

C'est un bon exemple de ce qu'il faudra ameliorer : quand la question vise explicitement une lettre, le systeme devrait probablement favoriser la correspondance.

### Reponse possible

Dans le corpus actuel, la lettre concernee est disponible sous forme de traduction francaise de travail, pas comme texte francais original garanti.

Elle est utile pour donner au chatbot une matiere de ton et de situation : Montaigne s'adresse a sa femme, dans un contexte lie a la consolation et a la publication de textes de La Boetie. En revanche, elle ne doit pas etre utilisee comme citation francaise authentique sans verification.

Pour une reponse finale, le chatbot devrait donc dire quelque chose comme :

> Dans la lettre adressee a sa femme, disponible ici en traduction de travail, Montaigne adopte un ton domestique, retenu et moral. Le passage peut servir a nourrir une reponse sur la consolation, mais il faut eviter de le citer comme un original francais certain.

## Question 3 - meme intention, mais reformulee avec des mots-ponts

### Question

> colere conversation moderation repondre sans se facher

### Morceaux retrouves

1. `essais` / `De la colere`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-31-de-la-colere/montaigne_essais_02_31_004.md`

2. `essais` / `De la conversation`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-08-de-la-conversation/montaigne_essais_03_08_007.md`

3. `essais` / `De la conversation`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-03/chapitre-08-de-la-conversation/montaigne_essais_03_08_004.md`

4. `essais` / `De la colere`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-31-de-la-colere/montaigne_essais_02_31_008.md`

5. `essais` / `De la colere`  
   `authors/montaigne/works/essais/chunks-michaud-modern/livre-02/chapitre-31-de-la-colere/montaigne_essais_02_31_005.md`

### Lecture du resultat

Cette recherche est beaucoup plus propre.

La question moderne a ete reformulee avec des mots qui font pont entre notre usage actuel et le vocabulaire du corpus : `colere`, `conversation`, `moderation`, `sans se facher`.

Cela montre probablement la prochaine brique a construire : une etape de reformulation automatique avant la recherche.

### Reponse possible

Pour repondre sans se facher, il faut d'abord refuser de prendre la colere pour un argument.

Montaigne est utile ici parce qu'il ne cherche pas une posture de saintete : il sait que la colere arrive, qu'elle peut emporter le jugement, et qu'elle aime se donner raison. La bonne conduite n'est donc pas de nier l'irritation, mais de l'empecher de conduire toute la reponse.

Une reponse inspiree par ces passages pourrait etre :

> Je ne veux pas ajouter une querelle au probleme. Dites-moi exactement ce qui vous a deplaise ; je regarderai ce qui depend de nous, et je vous repondrai sur les faits plutot que sur l'emportement du moment.

## Conclusion de la demo

La base fonctionne deja pour retrouver des passages utiles.

Mais pour obtenir un chatbot agreable, il ne faut pas seulement brancher le corpus brut sur un modele. Il faut ajouter au moins deux etapes :

1. reformuler la question moderne en mots-ponts compatibles avec le corpus ;
2. reranker les resultats pour garder les passages les plus utiles a la reponse.


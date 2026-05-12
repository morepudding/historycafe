from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "authors" / "montaigne" / "correspondence" / "chunks-fr-ai-draft"


LETTERS: dict[int, dict[str, object]] = {
    2: {
        "roman": "II",
        "title": "A Monsieur de Montaigne, son pere, dedicace de Raymond Sebond",
        "chunks": [
            """A Monseigneur, Monseigneur de MONTAIGNE.

[Cette lettre precede la traduction par Montaigne de la Theologie naturelle de Raymond de Sebond, imprimee a Paris en 1569.]

Suivant l'ordre que vous me donnates l'an passe dans votre maison de Montaigne, Monseigneur, j'ai revetu de francais, de ma propre main, Raymond de Sebond, ce grand theologien et philosophe espagnol ; et je l'ai depouille, autant que je l'ai pu, de cette mine rude et de cette apparence barbare sous lesquelles vous l'aviez d'abord vu. Il me semble qu'il est maintenant en etat de se presenter dans la meilleure compagnie.

Il se pourra bien que quelques esprits delicats remarquent encore dans ce livre quelque trace de parente gasconne ; mais ce sera d'autant plus a leur honte qu'ils auront laisse tomber cette tache sur un homme tout novice en ces matieres. Il est juste, Monseigneur, que l'ouvrage paraisse sous vos auspices, puisque tout ce qu'il peut avoir recu de correction et de poli vous est du.

Je vois pourtant bien que, si vous voulez regler vos comptes avec l'auteur, vous vous trouverez fort son debiteur ; car, en face de ses excellents et religieux discours, de ses conceptions hautes et pour ainsi dire divines, vous n'aurez a mettre que des mots et des phrases : marchandise si ordinaire et si commune que celui qui en possede le plus est peut-etre le plus mal partage.

Monseigneur, je prie Dieu qu'il vous donne une tres longue et tres heureuse vie. De Paris, ce 18 juin 1568. Votre tres humble et tres obeissant fils,

MICHEL DE MONTAIGNE"""
        ],
    },
    3: {
        "roman": "III",
        "title": "A Monsieur de Lansac",
        "chunks": [
            """A Monsieur, Monsieur de LANSAC, chevalier de l'ordre du Roi, conseiller prive, controleur general de ses finances, et capitaine des Cent-Gardes de sa maison.

[Cette lettre semble appartenir a l'annee 1570.]

MONSIEUR, je vous envoie l'Economique de Xenophon, mise en francais par feu Monsieur de La Boetie, present qui me parait convenable, tant parce que c'est l'ouvrage d'un gentilhomme de marque, illustre dans la guerre comme dans la paix, que parce qu'il a recu sa seconde forme d'un personnage que je sais avoir ete cher a votre affection durant sa vie.

Cela vous donnera occasion de continuer envers sa memoire la bonne opinion et la bienveillance que vous lui portiez. Et, pour parler franchement avec vous, Monsieur, ne craignez pas de les augmenter encore : car, n'ayant connu ses hautes qualites que dans sa vie publique, il m'appartient de vous assurer combien il possedait de dons au-dela de ce que vous avez pu personnellement eprouver de lui.

Il me fit l'honneur, tandis qu'il vivait, et je compte cela parmi les plus heureuses rencontres de ma vie, d'avoir avec moi une amitie si etroite et si intimement nouee qu'aucun mouvement, aucun elan, aucune pensee de son esprit ne m'etait cache. Si je ne l'ai pas bien juge, il faut l'attribuer a ma propre insuffisance. En verite, sans exagerer, il etait si pres du prodige que je crains de n'etre pas cru quand je parle de lui, meme en restant bien au-dessous de ce que j'ai connu.

Pour cette fois, Monsieur, je me contenterai de vous prier, pour l'honneur et le respect que nous devons a la verite, de temoigner et de croire que notre Guyenne n'a jamais vu son pareil parmi les hommes de sa profession. Dans l'espoir donc que vous lui rendrez ce qui lui est du, et afin de le rafraichir dans votre memoire, je vous presente ce livre, qui repondra pour moi que, si mon pouvoir n'etait insuffisant, je vous offrirais aussi volontiers quelque chose de moi-meme, en reconnaissance des obligations que je vous ai et de l'ancienne faveur et amitie que vous avez portees aux gens de notre maison. Mais, Monsieur, faute de meilleure monnaie, je vous offre en paiement l'assurance de mon desir de vous rendre humble service.

Monsieur, je prie Dieu qu'il vous ait en sa garde. Votre obeissant serviteur,

MICHEL DE MONTAIGNE."""
        ],
    },
    4: {
        "roman": "IV",
        "title": "A Monsieur de Mesmes",
        "chunks": [
            """A Monsieur, Monsieur de MESMES, seigneur de Roissy et de Malassize, conseiller prive du Roi.

MONSIEUR, c'est une des folies les plus visibles des hommes que d'employer la force de leur entendement a renverser et detruire les opinions communement recues parmi nous, et qui nous donnent repos et contentement. Car, tandis que tout ce qui est sous le ciel se sert des voies et moyens que la nature lui a donnes pour l'avancement et la commodite de son etre, ceux-ci, afin de paraitre d'un esprit plus vif et plus eclaire, ne recevant rien qui n'ait ete mille fois essaye et pese par le raisonnement le plus subtil, sacrifient leur paix interieure au doute, a l'inquietude et a l'agitation.

Ce n'est pas sans raison que l'enfance et la simplicite ont ete recommandees par l'Ecriture elle-meme. Pour moi, j'aime mieux etre en repos qu'habile : donnez-moi le contentement, quand meme mon esprit aurait moins d'etendue. Voila pourquoi, Monsieur, bien que les gens ingenieux se rient de notre soin pour ce qui arrivera apres nous, par exemple a nos ames, lesquelles, logees ailleurs, perdront toute connaissance de ce qui se passe ici-bas, je tiens pourtant pour une grande consolation de la fragilite et de la brievete de la vie de penser que nous avons pouvoir de la prolonger par la reputation et par la gloire. J'embrasse donc volontiers cette opinion douce et favorable a notre etre, sans rechercher trop curieusement comment ni pourquoi elle est vraie.

Ainsi, ayant aime plus que toute chose feu Monsieur de La Boetie, le plus grand homme, a mon jugement, de notre siecle, je me tiendrais pour fort negligent envers mon devoir si je ne faisais tout ce qui est en mon pouvoir pour empecher qu'un tel nom, et une memoire si digne d'etre conservee, ne tombassent dans l'oubli, et si je ne m'efforcais de les tenir vivants. Je crois qu'il sent quelque chose de ce que je fais pour lui, et que mes services le touchent et le rejouissent. En effet, il vit dans mon coeur si vivement et si entierement que j'ai peine a le croire livre a la terre muette, ou tout a fait retranche de notre commerce.

Puis donc, Monsieur, que toute nouvelle lumiere que je puis repandre sur lui et sur son nom ajoute quelque chose a sa seconde vie, et que son nom est ennobli et honore par le lieu qui le recoit, il m'appartient non seulement de l'etendre autant que je puis, mais encore de le confier a la garde de personnes d'honneur et de vertu. Vous tenez entre elles un rang tel que, pour vous donner occasion de recevoir ce nouvel hote et de lui faire bon accueil, j'ai resolu de vous presenter ce petit ouvrage. Ce n'est pas pour le profit que vous en pourriez tirer, sachant bien que vous n'avez pas besoin qu'on vous interprete Plutarque et ses semblables ; mais il se peut que Madame de Roissy, y lisant l'ordre du gouvernement domestique et de votre heureuse union peints au vif, prenne plaisir a voir combien son inclination naturelle a non seulement atteint, mais depasse les theories des plus sages philosophes touchant les devoirs et les lois de l'etat du mariage.

Et, en tout cas, ce me sera toujours honneur de pouvoir faire quelque chose qui soit au plaisir de vous et des votres, a cause de l'obligation ou je suis de vous servir.

Monsieur, je prie Dieu qu'il vous donne longue et heureuse vie. De Montaigne, ce 30 avril 1570. Votre humble serviteur,

MICHEL DE MONTAIGNE."""
        ],
    },
    5: {
        "roman": "V",
        "title": "A Monsieur de L'Hospital",
        "chunks": [
            """A Monsieur, Monsieur de L'HOSPITAL, chancelier de France.

MONSEIGNEUR, je suis d'avis que les personnes telles que vous, a qui la fortune et la raison ont commis la charge des affaires publiques, ne sont curieuses de rien davantage que de connaitre le caractere de ceux qui exercent les offices sous elles. Car il n'est point de societe si pauvrement pourvue que, si l'autorite y est bien distribuee, elle ne possede des personnes suffisantes pour remplir toutes les charges ; et, quand il en est ainsi, rien ne manque a la parfaite constitution d'un Etat.

Or, autant cela est desirable, autant il est difficile de l'accomplir, puisque vous ne pouvez avoir des yeux pour embrasser une multitude si vaste et si dispersee, ni pour voir jusqu'au fond des coeurs, afin d'y decouvrir les intentions et les consciences, qui sont les principales choses a considerer. Aussi n'y eut-il jamais republique si bien ordonnee qu'on n'y puisse souvent remarquer quelque defaut en tel departement ou tel choix ; et dans les regimes ou regnent l'ignorance et la malice, la faveur, l'intrigue et la violence, si quelque election se fait par merite et selon l'ordre, nous pouvons sans doute remercier la Fortune qui, dans ses mouvements capricieux, aura pris pour une fois le chemin de la raison.

Cette consideration, Monseigneur, m'a souvent console lorsque je voyais Monsieur Etienne de La Boetie, l'un des hommes les plus propres aux grandes charges de France, passer toute sa vie sans emploi ni reconnaissance, pres de son foyer domestique, au grand dommage du public. Pour ce qui le regardait, je puis vous assurer, Monseigneur, qu'il etait si riche de ces biens qui defient la fortune que jamais homme ne fut plus satisfait ni plus content. Je sais bien qu'il fut eleve aux dignites de son voisinage, dignites tenues pour considerables ; et je sais aussi que nul ne s'en acquitta jamais mieux, et qu'en mourant a trente-deux ans il jouissait, en cela, d'une reputation superieure a tous ceux qui l'avaient precede.

Mais, pour autant, ce n'est pas raison de laisser simple soldat celui qui merite d'etre capitaine, ni de donner de basses fonctions a ceux qui sont parfaitement capables des plus hautes. En verite, ses forces furent mal menagees et trop peu employees ; de sorte qu'au-dela de ce qu'il fit, il restait en lui une abondante capacite oisive qui aurait pu etre appelee au service, pour l'avantage public et pour sa propre gloire.

Ainsi donc, Monseigneur, puisqu'il etait si indifferent a sa propre renommee, car la vertu et l'ambition logent malheureusement rarement ensemble, et puisqu'il vecut dans un age ou les autres etaient trop lents ou trop jaloux pour rendre temoignage de ce qu'il etait, j'ai merveilleusement a coeur que sa memoire du moins, a laquelle je dois les offices d'un ami, recoive la recompense de sa belle vie, et qu'elle survive dans l'estime des hommes d'honneur et de vertu. C'est pourquoi, Monsieur, j'ai desire mettre en lumiere et vous presenter les quelques vers latins qu'il a laisses. A la difference du batisseur, qui tourne vers la rue la partie la plus agreable de sa maison, et du drapier, qui montre en vitrine sa meilleure marchandise, ce qu'il y avait de plus precieux dans mon ami, le suc et la moelle de son genie, est parti avec lui ; il ne nous est demeure que l'ecorce et les feuilles.""",
            """Les mouvements si justement regles de son esprit, sa piete, sa vertu, sa justice, sa vivacite, la solidite et la surete de son jugement, la hauteur de ses idees, elevees si loin au-dessus du commun, son savoir, la grace qui accompagnait ses actions les plus ordinaires, la tendre affection qu'il portait a son miserable pays, et sa supreme et juree detestation de tout vice, principalement de ce trafic villain qui se couvre du nom honorable de justice, devraient certainement inspirer a toutes les ames bien nees un amour singulier pour lui et un regret extraordinaire de sa perte.

Mais, Monsieur, je ne puis rendre justice a toutes ces qualites ; et, des fruits de ses propres etudes, il ne lui etait pas venu a l'esprit de laisser quelque preuve a la posterite. Tout ce qui reste est le peu qu'il fit par delassement et par intervalles.

Quoi qu'il en soit, je vous prie, Monsieur, de le recevoir avec bienveillance. Comme notre jugement sur les grandes choses se forme souvent a partir des petites, et comme les recreations memes des hommes illustres portent, aux yeux des bons observateurs, quelque trait honorable de leur origine, je voudrais que vous tiriez de ceci quelque connaissance de lui, et que vous cherissiez par la son nom et sa memoire. En cela, Monsieur, vous ne ferez que rendre l'estime qu'il avait de votre vertu, et realiser ce qu'il desira infiniment durant sa vie ; car il n'y avait personne au monde en la connaissance et l'amitie de qui il eut ete si heureux de se voir etabli que dans les votres.

Si quelqu'un s'offense de la liberte que je prends avec les biens d'autrui, je puis lui dire que rien de ce qui a ete ecrit ou pose, meme dans les ecoles de philosophie, touchant les droits et devoirs sacres de l'amitie, ne saurait donner une idee suffisante des rapports qui furent entre ce personnage et moi.

Au surplus, Monsieur, ce faible present, pour faire deux coups d'une pierre, pourra aussi, s'il vous plait, temoigner l'honneur et le respect que je porte a votre esprit et a vos hautes qualites ; car, quant aux dons adventices et accidentels, il n'est pas de mon gout d'en faire grand compte.

Monsieur, je prie Dieu qu'il vous donne tres heureuse et tres longue vie. De Montaigne, ce 30 avril 1570. Votre humble et obeissant serviteur,

MICHEL DE MONTAIGNE."""
        ],
    },
    6: {
        "roman": "VI",
        "title": "A Monsieur de Foix",
        "chunks": [
            """A Monsieur, Monsieur de FOIX, conseiller prive et ambassadeur de Sa Majeste aupres de la Seigneurie de Venise.

[Imprime avant les Vers francais d'Etienne de La Boetie, Paris, in-8, 1572.]

MONSIEUR, etant sur le point de recommander a vous et a la posterite la memoire de feu Etienne de La Boetie, tant pour son extreme vertu que pour l'affection singuliere qu'il me porta, il m'a semble que la coutume souvent pratiquee de derober a la vertu la gloire, sa fidele compagne, pour la donner, selon nos interets particuliers et sans discernement, au premier venu, etait une imprudence fort grave dans ses effets, et qui meriterait quelque contrainte de nos lois. Car nos deux principaux freins sont la recompense et la punition ; elles ne nous touchent proprement, et comme hommes, que par le moyen de l'honneur et du deshonneur, puisque ceux-ci penetrent l'esprit et atteignent nos sentiments les plus intimes, alors que les betes memes sont plus ou moins sensibles aux autres especes de recompenses et de chatiments corporels.

Il faut encore remarquer que l'habitude de louer la vertu, meme chez ceux qui ne sont plus avec nous, quoique cette louange leur soit impalpable, sert d'aiguillon aux vivants pour imiter leur exemple ; de meme que les sentences capitales sont executees par la loi davantage pour avertir les autres que pour ceux qui les subissent. Or, la louange et son contraire etant analogues par leurs effets, on ne peut guere nier que, si la loi defend de noircir la reputation d'autrui, elle ne nous empeche pas assez de donner de la reputation sans cause. Cette licence pernicieuse dans la distribution des louanges fut autrefois contenue dans de plus etroites limites ; et c'est peut-etre pourquoi la poesie perdit jadis credit aupres des plus judicieux.

Quoi qu'il en soit, on ne peut cacher que le vice du mensonge sied tres mal a un gentilhomme, quelque figure qu'il prenne.

Quant au personnage dont je vous parle, Monsieur, il m'eloigne beaucoup de ce langage ; car le danger, pour lui, n'est pas que je lui prete quelque chose, mais que je lui en retranche. Et c'est son malheur que, m'ayant fourni autant qu'un homme pouvait le faire de justes et manifestes occasions de louange, je me trouve incapable et impropre a la lui rendre, moi qui lui dois tant de vives communications et qui seul puis repondre d'un million d'accomplissements, de perfections et de vertus cachees, grace a ses etoiles contraires, dans une ame si noble.

Car la nature des choses ayant permis, je ne sais comment, que la verite, si belle et recevable qu'elle soit d'elle-meme, ne soit recue que lorsqu'il y a des arts de persuasion pour l'insinuer dans nos esprits, je me vois si depourvu, tant d'autorite pour soutenir mon simple temoignage que d'eloquence pour lui donner valeur et poids, que j'etais pres d'abandonner l'entreprise, n'ayant rien de lui qui me permit de montrer au monde une preuve de son genie et de son savoir.""",
            """En verite, Monsieur, surpris par son destin dans la fleur de l'age et dans la pleine possession de la sante la plus vigoureuse, il avait dessein de publier un jour des ouvrages qui auraient montre a la posterite quel homme il etait ; et peut-etre etait-il assez indifferent a la gloire pour avoir forme un tel projet en son esprit sans aller plus loin.

Mais j'ai conclu qu'il etait beaucoup plus excusable a lui d'ensevelir avec lui tous ses rares dons qu'il ne le serait a moi d'ensevelir aussi avec moi la connaissance que j'en avais recue. C'est pourquoi, ayant soigneusement rassemble tous les restes que j'ai trouves epars ca et la parmi ses papiers, j'ai dessein de les distribuer de facon a recommander sa memoire au plus grand nombre de personnes possible, choisissant les plus convenables et les plus dignes de ma connaissance, et celles dont le temoignage pourrait lui faire le plus d'honneur : telles que vous, Monsieur, qui avez peut-etre eu quelque connaissance de lui de son vivant, mais assurement trop faible pour decouvrir toute l'etendue de sa valeur.

La posterite me croira, si elle veut, lorsque je jure sur ma conscience que je l'ai connu et vu tel que, tout considere, je ne pourrais ni desirer ni imaginer un esprit qui surpassat le sien.

Je vous prie tres humblement, Monsieur, de prendre non seulement son nom sous votre protection generale, mais encore ces dix ou douze stances francaises, qui se placent comme d'elles-memes a l'ombre de votre patronage. Car je ne vous cacherai pas que leur publication fut differee, a la parution de ses autres ecrits, sous pretexte, disait-on la-bas a Paris, qu'elles etaient trop crues pour voir le jour. Vous jugerez, Monsieur, combien il y a de verite en cela. Et puisqu'on pense que, par ici, rien ne peut se produire dans notre dialecte qui ne soit barbare et mal poli, il vous revient, vous qui, outre votre rang de premiere maison de Guyenne, descendu de vos ancetres, possedez encore toute sorte d'autres qualites, d'etablir, non seulement par votre exemple, mais par votre temoignage autorise, qu'il n'en est pas toujours ainsi. D'autant plus que, s'il est plus naturel aux Gascons d'agir que de parler, il leur arrive pourtant d'employer la langue plus que le bras, et l'esprit a la place de la valeur.""",
            """Pour ma part, Monsieur, il n'est pas de mon metier de juger de telles matieres ; mais j'ai entendu des personnes supposees s'y connaitre dire que ces stances sont non seulement dignes d'etre presentees sur la place publique, mais encore, quant a la beaute et a la richesse de l'invention, pleines de moelle et de matiere autant qu'aucune composition de ce genre parue dans notre langue.

Naturellement, chaque ouvrier se sent plus fort en quelque partie speciale de son art, et les plus heureux sont ceux qui mettent la main sur la plus noble ; car toutes les parties necessaires a la construction d'un tout ne sont pas egalement precieuses. On trouvera peut-etre ailleurs plus de delicatesse dans la phrase, plus de douceur et d'harmonie dans le langage ; mais pour la grace imaginative et pour l'abondance d'esprit aigu, je ne pense pas qu'il ait ete surpasse. Il faut encore tenir compte de ce qu'il ne faisait de ces choses ni son occupation ni son etude, et qu'il ne prenait guere la plume en main plus d'une fois l'an, comme le montre la tres faible quantite de ses restes.

Vous voyez donc ici, Monsieur, bois vert et bois sec, sans aucune sorte de choix, tout ce qui est venu en ma possession ; si bien qu'il y a parmi le reste des essais meme de son enfance. En verite, il semble les avoir ecrits seulement pour montrer qu'il etait capable de traiter tous les sujets ; car autrement, mille fois dans la conversation ordinaire, je lui ai entendu echapper des choses infiniment plus dignes d'etre admirees et conservees.

Voila, Monsieur, ce que la justice et l'affection, formant ici une rare conjonction, m'obligent a dire de ce grand et bon homme. Si j'ai offense en quelque chose par la liberte que j'ai prise de m'adresser a vous sur un tel sujet et avec tant d'etendue, veuillez vous souvenir que le principal effet de la grandeur et de l'eminence est d'exposer celui qui les possede aux appels importuns du reste du monde.

Sur ce, apres vous avoir offert mon affection devouee a votre service, je supplie Dieu de vous donner, Monsieur, une vie heureuse et longue. De Montaigne, ce 1er septembre 1570. Votre obeissant serviteur,

MICHEL DE MONTAIGNE."""
        ],
    },
    7: {
        "roman": "VII",
        "title": "A sa femme",
        "chunks": [
            """A Mademoiselle de MONTAIGNE, ma femme.

[Imprime comme preface a la Consolation de Plutarque a sa femme, publiee par Montaigne avec plusieurs autres textes de La Boetie vers 1571.]

MA FEMME, vous savez bien qu'il ne convient pas, selon les regles de notre temps, a un homme du monde de continuer a vous faire la cour et a vous caresser ; car on dit qu'une personne sensee peut bien prendre femme, mais qu'epouser sa femme est agir en sot. Qu'ils parlent. Pour moi, je m'en tiens a la coutume du bon vieux temps ; je porte aussi mes cheveux comme on les portait alors. Et, en verite, la nouveaute coute jusqu'a present si cher a ce pauvre pays, et je ne sais si nous en avons encore atteint le plus haut point, que partout et en toutes choses je renonce a la mode. Vivons, ma femme, vous et moi, a l'ancienne francaise.

Vous vous souvenez peut-etre que feu Monsieur de La Boetie, mon frere et inseparable compagnon, me donna sur son lit de mort tous ses livres et papiers, qui sont demeures depuis la plus precieuse part de mes biens. Je ne veux pas les garder chichement pour moi seul, et je ne merite pas d'en avoir l'usage exclusif ; j'ai donc resolu de les communiquer a mes amis. Et comme je n'en ai point, je crois, de plus particulierement intime que vous, je vous envoie la Lettre de consolation que Plutarque ecrivit a sa femme, traduite en francais par lui.

Je regrette fort que la fortune vous en ait fait un present si approprie, et que, n'ayant eu qu'un enfant, et encore une fille longtemps attendue apres quatre ans de mariage, il vous ait fallu la perdre en sa seconde annee. Mais je laisse a Plutarque le soin de vous consoler et de vous apprendre votre devoir en cela ; je vous prie de vous fier a lui pour l'amour de moi, car il vous revelera mes propres pensees et exprimera la chose bien mieux que je ne saurais le faire.

Sur ce, ma femme, je me recommande tres cordialement a votre bonne volonte, et prie Dieu qu'il vous ait en sa garde.

De Paris, ce 10 septembre 1570. Votre bon mari,

MICHEL DE MONTAIGNE."""
        ],
    },
    8: {
        "roman": "VIII",
        "title": "A Monsieur Dupuy",
        "chunks": [
            """A Monsieur DUPUY, conseiller du Roi en sa cour et parlement de Paris.

[Il s'agit probablement de Claude Dupuy, ne a Paris en 1545, l'un des quatorze juges envoyes en Guyenne apres le traite de Fleix en 1580. C'est peut-etre dans ces circonstances que Montaigne lui adressa cette lettre.]

MONSIEUR, l'affaire du sieur de Verres, prisonnier, qui m'est extremement connu, merite, dans la decision qu'on en prendra, l'exercice de la clemence qui vous est naturelle, si l'interet public vous permet justement d'y avoir recours. Il a fait une chose non seulement excusable selon les lois militaires de ce temps, mais necessaire et, a notre avis, louable. Il l'a faite sans doute a regret et par contrainte ; il n'y a aucun autre passage de sa vie qui soit ouvert au reproche.

Je vous supplie, Monsieur, de donner a cette affaire votre attentive consideration ; vous trouverez qu'elle est telle que je vous la represente. On le poursuit pour ce crime d'une maniere bien pire que l'offense elle-meme. S'il peut lui etre utile, je desire vous faire savoir que c'est un homme eleve dans ma maison, allie a plusieurs familles honorables, et quelqu'un qui, ayant mene une vie honnete, est mon ami particulier.

En le sauvant, vous m'obligerez extremement. Je vous prie tres humblement de le tenir pour recommande par moi ; et, apres vous avoir baise les mains, je prie Dieu, Monsieur, qu'il vous donne longue et heureuse vie.

De Castera, ce 23 avril [1580]. Votre affectionne serviteur,

MONTAIGNE."""
        ],
    },
    9: {
        "roman": "IX",
        "title": "Aux jurats de Bordeaux",
        "chunks": [
            """Aux jurats de Bordeaux.

[Publie d'apres l'original conserve aux archives de la ville de Bordeaux par M. Gustave Brunet dans le Bulletin du Bibliophile, juillet 1839.]

MESSIEURS, j'espere que le voyage de Monsieur de Cursol sera profitable a la ville. Ayant en main une cause si juste et si favorable, vous avez fait tout votre possible pour mettre l'affaire en bon etat ; et les choses etant ainsi bien disposees, je vous prie d'excuser encore pour quelque temps mon absence. J'abregerai mon sejour autant que la pression de mes affaires me le permettra.

J'espere que le delai sera court. Cependant, vous me garderez, s'il vous plait, en votre bonne grace, et me commanderez, si l'occasion s'en presente, en m'employant au service public et au votre. Monsieur de Cursol m'a aussi ecrit et m'a averti de son voyage.

Je me recommande humblement a vous, et prie Dieu, Messieurs, qu'il vous donne longue et heureuse vie. De Montaigne, ce 21 mai 1582. Votre humble frere et serviteur,

MONTAIGNE."""
        ],
    },
    10: {
        "roman": "X",
        "title": "Aux jurats de Bordeaux",
        "chunks": [
            """Aux memes.

[L'original est conserve aux archives de Toulouse.]

MESSIEURS, j'ai pris ma juste part de la satisfaction que vous me dites eprouver du bon expediment de votre affaire, selon le rapport de vos deputes ; et je tiens pour un signe favorable que vous ayez donne a l'annee un commencement si heureux. J'espere me joindre a vous a la premiere occasion convenable.

Je me recommande tres humblement a votre gracieuse consideration, et prie Dieu de vous donner, Messieurs, une heureuse et longue vie. De Montaigne, ce 8 fevrier 1585. Votre humble frere et serviteur,

MONTAIGNE."""
        ],
    },
    11: {
        "roman": "XI",
        "title": "Aux jurats de Bordeaux",
        "chunks": [
            """Aux memes.

MESSIEURS, j'ai recu ici de vos nouvelles par Monsieur le Marechal. Je n'epargnerai ni ma vie ni aucune autre chose pour votre service, et je vous laisse juges de savoir si l'aide que je pourrais rendre par ma presence a la prochaine election vaudrait le risque que je courrais en entrant dans la ville, vu le mauvais etat ou elle se trouve, particulierement pour des gens venant d'un air aussi sain que celui ou je suis.

[Il s'agit de la peste qui sevissait alors et qui emporta 14 000 personnes a Bordeaux.]

Je m'approcherai de vous mercredi autant que je pourrai, c'est-a-dire jusqu'a Feuillas, si la maladie n'a pas gagne ce lieu. Comme je l'ecris a Monsieur de La Molte, j'y serai tres aise d'avoir l'honneur de voir l'un de vous pour recevoir vos directives, et pour me decharger des lettres de creance que Monsieur le Marechal me remettra pour vous tous.

Sur ce, je me recommande humblement a votre bonne grace, et prie Dieu de vous donner, Messieurs, longue et heureuse vie. A Libourne, ce 30 juillet 1585. Votre humble serviteur et frere,

MONTAIGNE."""
        ],
    },
    12: {
        "roman": "XII",
        "title": "Lettre politique attribuee a Montaigne",
        "chunks": [
            """[Selon le docteur Payen, cette lettre appartient a 1588. Son authenticite a ete contestee, mais a tort selon l'editeur anglais. Il ne semble pas que l'on sache a qui elle fut adressee.]

MONSEIGNEUR, vous avez appris que nos bagages nous ont ete enleves sous les yeux dans la foret de Villebois ; puis, apres beaucoup de discussions et de delais, que la prise a ete declaree illegale par le Prince. Nous n'avons pourtant pas ose poursuivre notre chemin, faute d'assurance sur la surete de nos personnes, qui aurait du etre clairement exprimee dans nos passeports.

La Ligue a fait cela, Monsieur de Barrant et Monsieur de La Rochefoucauld ; l'orage est tombe sur moi, qui avais mon argent dans ma caisse. Je n'en ai rien recouvre, et la plus grande part de mes papiers et de mon argent demeure entre leurs mains.

Je n'ai pas vu le Prince. Cinquante furent perdus... Quant au comte de Thorigny, il perdit quelque vaisselle d'argent et quelques vetements. Il se detourna de sa route pour visiter les dames en deuil a Montresor, ou sont les restes de ses deux freres et de sa grand-mere, et il nous rejoignit en cette ville, d'ou nous reprendrons bientot notre voyage.

Le voyage de Normandie est remis. Le Roi a depeche Messieurs de Bellievre et de La Guiche vers Monsieur de Guise pour le sommer de venir a la cour ; nous y serons jeudi.

D'Orleans, ce 16 fevrier, au matin [1588-1589 ?]. Votre tres humble serviteur,

MONTAIGNE."""
        ],
    },
    13: {
        "roman": "XIII",
        "title": "A Mademoiselle Paulmier",
        "chunks": [
            """A Mademoiselle PAULMIER.

[Cette lettre, au moment de la publication de l'edition variorum de 1854, semble avoir ete entre des mains privees.]

MADEMOISELLE, mes amis savent que, des le premier moment de notre connaissance, je vous avais destine un exemplaire de mon livre ; car je sens que vous lui avez fait beaucoup d'honneur. La courtoisie de Monsieur Paulmier m'oterait maintenant le plaisir de vous le donner, puisqu'il m'a oblige depuis bien au-dela de la valeur de mon livre.

Vous l'accepterez donc, s'il vous plait, comme vous appartenant deja avant que je vous le dusse ; et vous me ferez la faveur de l'aimer, soit pour lui-meme, soit pour moi. Je garderai ma dette envers Monsieur Paulmier non acquittee, afin de la lui rendre si j'ai quelque autre jour moyen de le servir."""
        ],
    },
    14: {
        "roman": "XIV",
        "title": "A Henri IV",
        "chunks": [
            """Au ROI, HENRI IV.

[L'original se trouve a la Bibliotheque nationale de France, dans la collection Dupuy. Il fut decouvert par M. Achille Jubinal, qui l'imprima en 1850 avec un fac-simile entier de l'autographe.]""",
            """SIRE, c'est etre au-dessus du poids et de la foule de vos grandes et importantes affaires que de savoir, comme vous le faites, vous preter et vous appliquer aux petites choses en leur tour, selon le devoir de votre dignite royale, qui vous expose en tout temps a toute sorte et degre de personnes et d'emplois. Mais que Votre Majeste ait daigne considerer ma lettre et commander qu'on y repondit, j'aime mieux l'attribuer moins a votre grand entendement qu'a votre bonte de coeur.

J'ai toujours attendu avec joie que vous entrassiez en la fortune ou vous etes maintenant ; et vous pouvez vous souvenir que, meme lorsque j'avais a en faire confession a mon cure, je regardais vos succes avec satisfaction. Aujourd'hui, avec plus de propriete et de liberte, je les embrasse affectueusement. Ils vous servent la ou vous etes comme faits positifs ; mais ils ne nous servent pas moins ici par la renommee qu'ils repandent : l'echo porte autant que le coup.

Nous ne pourrions tirer de la justice de votre cause des arguments aussi puissants pour maintenir et ramener vos sujets que nous en tirons des nouvelles du succes de votre entreprise. Et je dois assurer Votre Majeste que les changements recents a votre avantage que vous observez par ici, et l'heureuse issue de vos affaires a Dieppe, ont opportunement seconde le zele honnete et la merveilleuse prudence de Monsieur le Marechal de Matignon. Je me flatte que vous ne recevez pas jour apres jour le recit de si bons et si remarquables services sans vous souvenir de mes assurances et de mes attentes.

J'attends de l'ete prochain non seulement les fruits que nous pourrons manger, mais ceux qui naitront de notre commune tranquillite ; et j'espere qu'il passera sur nos tetes avec le meme cours heureux, dissipant, comme ses predecesseurs, toutes les belles promesses dont vos adversaires soutiennent les esprits de leurs partisans. Les inclinations populaires ressemblent a une maree : si le courant commence une fois en votre faveur, il ira de lui-meme jusqu'au bout.

J'aurais beaucoup desire que le gain particulier des soldats de votre armee, et la necessite de les satisfaire, ne vous eussent pas prive, surtout dans cette ville principale, de la glorieuse reputation de traiter vos sujets rebelles, au milieu de la victoire, avec plus de clemence que leurs propres protecteurs. Ainsi, au lieu d'une renommee passagere et usurpee, vous leur auriez montre qu'ils etaient reellement les votres par l'exercice d'une protection vraiment paternelle et royale.

Dans la conduite d'affaires telles que celles que vous avez en main, les hommes sont contraints de recourir a des expedients extraordinaires. On voit toujours qu'elles sont surmontees par leur grandeur et leur difficulte ; quand il n'est pas facile d'achever la conquete par les armes et la force, la fin s'obtient par la clemence et la generosite, excellents appats pour attirer les hommes, surtout vers le parti juste et legitime. S'il doit y avoir severite et punition, qu'elles soient differees jusqu'a ce que le succes soit assure.

Un grand conquerant des temps passes se vantait de donner a ses ennemis autant de raison de l'aimer qu'a ses amis. Et deja nous sentons ici quelque effet de l'impression favorable produite sur nos villes rebelles par le contraste entre leur rude traitement et celui des villes qui vous sont loyales. Desirant a Votre Majeste un bonheur plus tangible et moins hasardeux, et que vous soyez aime plutot que craint de votre peuple, croyant que votre bien et le leur sont necessairement lies, je me rejouis de penser que le progres que vous faites va vers des conditions de paix plus praticables aussi bien que vers la victoire.""",
            """Sire, votre lettre du dernier novembre ne m'est arrivee qu'a l'instant, alors que le terme qu'il vous avait plu de me donner pour vous rencontrer a Tours etait deja passe. Je tiens pour une singuliere faveur que vous ayez daigne souhaiter la visite d'un homme si inutile, mais qui est tout a vous, et plus encore par affection que par devoir.

Vous avez fort louablement adapte vos dehors a votre nouvelle fortune ; mais la conservation de votre ancienne affabilite et franchise dans le commerce prive merite une egale louange. Vous avez daigne penser a mon age, autant qu'au desir que j'ai de vous voir en quelque lieu ou vous soyez delivre de ces laborieuses agitations. Ne sera-ce pas bientot a Paris, Sire ? Et que rien ne m'empeche alors de m'y presenter.

Votre tres humble et tres obeissant serviteur et sujet,

MONTAIGNE.

De Montaigne, ce 18 janvier [1590]."""
        ],
    },
    15: {
        "roman": "XV",
        "title": "A Henri IV",
        "chunks": [
            """Au meme.

[Cette lettre se trouve aussi dans la collection nationale, parmi les papiers Dupuy. Elle fut imprimee pour la premiere fois dans le Journal de l'Instruction publique, le 4 novembre 1846.]

SIRE, la lettre qu'il a plu a Votre Majeste de m'ecrire le 20 juillet ne m'a ete remise que ce matin, et m'a trouve couche d'une tres violente fievre tierce, maladie fort commune en ce pays depuis le mois dernier.

Sire, je me tiens grandement honore de recevoir vos commandements, et je n'ai pas manque de faire savoir a Monsieur le Marechal de Matignon, par trois fois et avec grande insistance, mon intention et mon obligation de me rendre aupres de lui, jusqu'a lui indiquer meme la route par laquelle je pensais le rejoindre secretement, s'il le jugeait bon. N'ayant recu aucune reponse, je pense qu'il a pese la difficulte et le risque du voyage pour moi.

Sire, Votre Majeste me fera la faveur de croire, s'il lui plait, que je ne me plaindrai jamais de la depense dans les occasions ou je n'hesiterais pas a employer ma vie. Je n'ai jamais tire aucun profit substantiel de la liberalite des rois, que je n'ai ni recherchee ni meritee ; et je n'ai recu aucune recompense des services que je leur ai rendus, dont Votre Majeste connait une partie. Ce que j'ai fait pour vos predecesseurs, je le ferai encore plus volontiers pour vous.

Je suis aussi riche, Sire, que je desire l'etre. Quand j'aurai epuise ma bourse en vous accompagnant a Paris, je prendrai la liberte de vous le dire ; et alors, si vous me jugez digne d'etre retenu plus longtemps dans votre suite, vous me trouverez plus modeste dans mes demandes que le plus humble de vos officiers.

Sire, je prie Dieu pour votre prosperite et votre sante. Votre tres humble et tres obeissant serviteur et sujet,

MONTAIGNE.

De Montaigne, ce 2 septembre [1590]."""
        ],
    },
    16: {
        "roman": "XVI",
        "title": "Au gouverneur de Guyenne",
        "chunks": [
            """Au gouverneur de Guyenne.""",
            """MONSEIGNEUR, j'ai recu ce matin votre lettre, que j'ai communiquee a Monsieur de Gourgues, et nous avons dine ensemble chez Monsieur [le maire] de Bordeaux. Quant a l'inconvenient de transporter l'argent nomme dans votre memoire, vous voyez combien il est difficile d'y pourvoir ; mais vous pouvez etre assure que nous le surveillerons d'aussi pres que possible.

J'ai fait tous mes efforts pour decouvrir l'homme dont vous parliez. Il n'a pas ete ici ; et Monsieur de Bordeaux m'a montre une lettre ou il dit qu'il n'a pu venir voir le directeur de Bordeaux comme il en avait l'intention, ayant ete averti que vous vous mefiez de lui. La lettre est d'avant-hier. Si j'avais pu le trouver, j'aurais peut-etre suivi une voie plus douce, incertain que j'etais de vos intentions ; mais je vous supplie neanmoins de ne concevoir aucun doute que je refuse d'executer aucun de vos souhaits, et que, quand il s'agit de vos commandements, je ne connais distinction ni de personne ni de chose.

J'espere que vous avez en Guyenne beaucoup de gens aussi bien affectionnes a vous que je le suis. On rapporte que les galeres de Nantes avancent vers Brouage. Monsieur le Marechal de Biron n'est pas encore parti. Ceux qui etaient charges de porter le message a Monsieur d'Usee disent qu'ils ne peuvent le trouver ; et je crois que, s'il a ete ici, il n'y est plus. Nous tenons un oeil vigilant sur nos portes et nos gardes, et nous les surveillons un peu plus attentivement en votre absence. Cela me rend inquiet non seulement pour la conservation de la ville, mais aussi pour vous-meme, sachant que les ennemis du roi sentent combien vous etes necessaire a son service, et combien nous prospererions mal sans vous.

Je crains que, dans le lieu ou vous etes, vous ne soyez assailli par tant d'affaires demandant votre attention de toutes parts qu'il vous faudra beaucoup de temps et de peine avant d'avoir tout dispose. S'il survient quelque nouvelle importante, je depecherai aussitot un expres ; et vous pourrez conclure que rien ne bouge si vous n'avez pas de mes nouvelles. Je vous prie toutefois de vous souvenir que les mouvements de cette sorte sont d'ordinaire si soudains et si inattendus que, s'ils arrivent, ils me saisiront a la gorge avant d'avoir dit un mot.

Je ferai ce que je pourrai pour recueillir des nouvelles, et, pour cela, je m'attacherai a visiter et voir des hommes de toute opinion. Jusqu'a present rien ne bouge. Monsieur de Londel m'a vu ce matin, et nous avons arrange quelques avances pour la place, ou j'irai demain matin.

Depuis que j'ai commence cette lettre, j'ai appris de Chartreux que deux gentilshommes, se disant au service de Monsieur de Guise et venant d'Agen, sont passes pres de Chartreux ; mais je n'ai pu savoir quelle route ils ont prise. On vous attend a Agen. Le sieur de Mauvesin est venu jusqu'a Canteloup, puis s'en est retourne, ayant obtenu quelque renseignement. Je cherche un capitaine Rous, a qui [...] a ecrit, essayant de l'attirer a sa cause par toutes sortes de promesses.

Le bruit des deux galeres de Nantes pretes a descendre sur Brouage est confirme comme certain ; elles portent deux compagnies de fantassins. Monsieur de Mercure est a Nantes. Le sieur de La Courbe a dit a Monsieur le president Nesmond que Monsieur d'Elbeuf est de ce cote d'Angers, et loge chez son pere. Il tire vers le Bas-Poitou avec 4000 fantassins et 400 ou 500 chevaux, ayant ete renforce par les troupes de Monsieur de Brissac et d'autres, et Monsieur de Mercure doit le rejoindre.

On dit aussi que Monsieur du Maine va prendre le commandement de toutes les forces qu'ils ont rassemblees en Auvergne, et qu'il traversera le Forez pour avancer vers le Rouergue et vers nous, c'est-a-dire vers le roi de Navarre, contre qui tout cela est dirige. Monsieur de Lansac est a Bourg et a deux vaisseaux de guerre qui restent a son service. Ses fonctions sont navales.

Je vous dis ce que j'apprends, et mele ensemble les bruits de ville plus ou moins probables avec les faits reels, afin que vous soyez en possession de tout.""",
            """MONTAIGNE.

Je n'ai vu personne de la part du roi de Navarre ; on dit que Monsieur de Biron l'a vu."""
        ],
    },
}


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for number, letter in LETTERS.items():
        roman = str(letter["roman"])
        chunks = list(letter["chunks"])
        letter_dir = OUT_DIR / f"letter-{number:02d}-{roman.lower()}"
        letter_dir.mkdir(parents=True, exist_ok=True)
        for index, body in enumerate(chunks, start=1):
            chunk_id = f"montaigne_letters_fr_ai_{number:02d}_{index:03d}"
            lines = [
                "---",
                f"chunk_id: {chunk_id}",
                "author_id: montaigne",
                "work_id: correspondence",
                "source_id: wikisource_en_letters_1877",
                "source_name: \"Wikisource EN\"",
                "source_url: \"https://en.wikisource.org/wiki/The_Essays_of_Montaigne/The_Letters_of_Montaigne\"",
                "rights: public_domain",
                "language: fr",
                "original_language: fr",
                "translated_from_language: en",
                "translation_status: ai_draft",
                "source_quality: useful_but_not_original",
                "text_type: letter_translation_fr_draft",
                f"letter_number: {number}",
                f"letter_roman: {yaml_quote(roman)}",
                f"letter_title_fr: {yaml_quote(str(letter['title']))}",
                f"chunk_index: {index}",
                f"chunk_count_in_letter: {len(chunks)}",
                f"word_count: {word_count(body)}",
                "use_for_voice: true",
                "use_for_exact_french_style: false",
                "use_for_direct_quote: false",
                "themes: []",
                "---",
                "",
            ]
            (letter_dir / f"{chunk_id}.md").write_text("\n".join(lines) + body + "\n", encoding="utf-8")
            total += 1

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "# Lettres de Montaigne - traduction francaise de travail\n\n"
        "Ce dossier contient une retraduction francaise de travail des lettres II a XVI importees depuis Wikisource EN.\n\n"
        "La lettre I existe deja en francais original dans `../chunks/lettre-mort-la-boetie/` et ne doit pas etre remplacee par une retraduction.\n\n"
        "Ces fichiers sont utiles pour le RAG en francais et pour la teinte de personnalite, mais ne doivent pas etre cites comme formulations originales de Montaigne.\n",
        encoding="utf-8",
    )
    print(f"Written French draft chunks: {total}")


if __name__ == "__main__":
    main()


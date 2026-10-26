# Auto Elden Ring — présentation complète du projet

🇬🇧 [Read in English](PROJECT.md)

Auto Elden Ring est un planificateur hors ligne pour Windows, conçu pour les joueurs
d'Elden Ring. Il indique ce dont ton personnage a besoin ensuite — attributs, niveaux,
améliorations d'armes, pierres de forge — et combien de temps il faudra pour farmer les
runes nécessaires à un objectif. Il tient un journal daté pour chaque personnage et peut
lire tes fichiers de sauvegarde PC sans jamais les modifier.

Tout fonctionne sur ton ordinateur : pas de compte, pas de connexion internet, pas de télémétrie.

## À quoi ça sert

- **Connaître le coût exact avant de dépenser.** Le prix en runes d'un niveau, d'une
  amélioration d'arme ou d'une pierre est calculé à partir des tables de coûts du jeu.
- **Planifier les prochaines étapes.** Choisis un niveau cible, une amélioration d'arme ou
  un stock de pierres, et vois ce qui est abordable et ce qu'il reste à farmer.
- **Estimer le farm de runes.** Mesure ton propre rythme de runes et obtiens une durée
  estimée pour atteindre un objectif.
- **Garder un historique.** Les checkpoints et les événements personnalisés gardent la
  trace de la progression d'un personnage dans le temps.
- **Importer ta progression.** Lis un fichier de sauvegarde PC pour remplir un personnage,
  en lecture seule.

C'est un outil de planification et un carnet. Il ne joue pas à ta place, ne lit pas la
mémoire du jeu en direct, ne modifie pas les sauvegardes et ne se synchronise pas entre
ordinateurs.

## Pour qui

Les joueurs d'Elden Ring qui veulent planifier leurs builds, leurs améliorations d'armes
et leur farm de runes, avec un outil local et hors ligne, ouvert à côté du jeu.

## Fonctionnalités principales

### Personnages et chronologies (le journal)

- Crée un personnage avec son nom en jeu et sa classe de départ d'origine.
- Une chronologie par personnage : des **checkpoints** (photos datées de l'état actuel) et
  des **événements personnalisés** (un état daté que tu saisis, avec attributs et armes).
- Parcours les longs historiques par pages de 100 événements au maximum.
- Ouvre n'importe quel checkpoint pour voir son niveau, ses runes, ses attributs, son
  équipement, ses armes, ses pierres et les changements depuis l'événement précédent. Un
  checkpoint enregistré ne change jamais par la suite.
- La bibliothèque peut contenir jusqu'à 100 personnages.

### Import et actualisation des sauvegardes

- Importe un fichier de sauvegarde PC (`.sl2` ou `.co2`). La lecture est en lecture seule :
  taille du fichier, date de modification et somme de contrôle de chaque emplacement sont
  vérifiées avant toute acceptation.
- Mémorise le dossier d'installation ou le fichier de sauvegarde, et jusqu'à 20 fichiers.
- Les données importées comprennent le nom, la classe de départ, les attributs, le niveau,
  les runes possédées, les armes du catalogue et leurs améliorations, les armures, les
  talismans, les objets, les objets clés et les pierres ordinaires.
- **Actualiser les sauvegardes** relit la dernière progression enregistrée en arrière-plan,
  sans changer la fenêtre ni tes objectifs. Seuls les changements significatifs créent un
  événement, donc les relectures répétées ne dupliquent pas l'historique.
- L'application voit la progression que le jeu a écrite sur le disque. La progression non
  sauvegardée dans le jeu n'est pas visible.

### Calculateur de personnage

- Saisis les attributs permanents actuels et cibles ; les deux niveaux se mettent à jour
  automatiquement.
- Vois le coût exact en runes des niveaux entre l'actuel et la cible, le montant déjà
  dépensé depuis le niveau de la classe de départ, le coût pour atteindre le niveau maximum
  (713), et le nombre de niveaux que tes runes permettent d'acheter.
- Les coûts viennent des tables entières fournies (version 1.17.1 du jeu, 712 passages de niveau).

### Améliorations d'armes

- **Par prix d'amélioration :** saisis le coût du forgeron pour la première amélioration,
  ou colle le prix de la suivante et l'application remonte au prix de base. Les frais de
  forge standard, sombres et spéciaux suivent les formules documentées dans
  [SOURCES.md](SOURCES.md).
- **Choisir des armes :** sélectionne des armes dans un catalogue illustré de 487 entrées
  réparties en 42 catégories, recherche-les, et règle pour chaque arme l'amélioration
  actuelle, la cible et le nombre d'exemplaires.
- **Maximum sans pierres de dragon ancien :** planifie toutes les améliorations atteignables
  avec les pierres ordinaires.
- Les améliorations déjà possédées d'une sauvegarde importée initialisent les armes choisies.

### Pierres de forge

- Enregistre ton stock de pierres, ou coche les achats effectués.
- Les runes possédées servent seulement à estimer le déficit de farm ; elles ne bloquent jamais un achat.
- Les pierres de dragon ancien n'ont ni prix ni stock inventés.

### Terminer des améliorations

Confirme les améliorations terminées dans le jeu : l'application amène les armes à leurs
cibles, remet à zéro les pierres ordinaires et les runes possédées, et enregistre un
événement dans le journal. Tout surplus réel peut être saisi à nouveau immédiatement.

### Farm de runes

- **Mesure d'une minute :** lance le minuteur, farme, puis saisis les runes gagnées.
- **Test complet :** trois essais séparés (60 s, 60 s et 180 s), chacun pondéré par sa durée.
- **Bonus :** compare les talismans et consommables utilisés pendant le test. Les bonus de
  découverte d'argent ne contribuent pas aux gains de runes dans le modèle (0 %).
- **Lieux de farm :** enregistre un lieu nommé avec son taux mesuré, et réutilise-le pour
  estimer le temps d'un objectif depuis les pages personnage et armes.
- Les projections dépendent du parcours, des temps morts, des arrondis et de l'activation
  des bonus ; ce sont des estimations.

### Vue équipement

Pour un personnage ou un checkpoint, la vue équipement affiche les six emplacements d'arme,
les quatre emplacements d'armure et les quatre emplacements de talisman, séparément de
toutes les armes acquises. Les quantités de l'inventaire et du coffre sont combinées. Les
noms d'objets et les petites icônes sont fournis avec l'application, donc la vue fonctionne hors ligne.

### Fenêtre compagnon

Une petite fenêtre sans bordure, toujours au premier plan, avec tes objectifs actuels :
niveaux, améliorations et farm, plus un compteur de runes modifiable. Tu peux la déplacer
n'importe où ; elle se cale sur les bords de l'écran. Tu peux revenir à la fenêtre complète à tout moment.

### Interface et accessibilité

- Deux styles visuels, chacun avec une palette fixe (voir plus bas).
- Six langues : anglais (par défaut), français, tchèque, allemand, espagnol et japonais,
  changeables instantanément dans les Paramètres.
- **Mode lecture** pour les lecteurs dyslexiques : police OpenDyslexic fournie, texte plus
  grand et palette crème. Le désactiver restaure ton style.
- Menus et boîtes de dialogue natifs de Windows, navigation au clavier comprise.
- Musique de fond locale (MP3, WAV, FLAC ou OGG) depuis un fichier de ton choix, avec lecture,
  pause et arrêt.

## Styles visuels

| Style | Apparence | Typographie | Couleurs |
| --- | --- | --- | --- |
| **Lisible** (par défaut) | Texte noir sur blanc, bordures visibles, accent bleu | Segoe UI | Fond `#F5F6F8`, cartes `#FFFFFF`, texte `#0F1419`, accent `#1E40AF` |
| **Carnet** | Journal de voyage sombre, cartes filetées, accent laiton | Constantia pour les titres, Bahnschrift pour l'interface | Fond `#121210`, cartes `#1B1A17`, texte `#E8DCC0`, accent `#B08D4E` |

Les deux styles gardent le texte et les bordures au niveau du WCAG AA. Mesures : texte
Lisible sur cartes 18,5:1, texte Carnet sur cartes 12,8:1, texte des boutons sur l'accent
8,7:1 et 6,0:1.

Les versions précédentes avaient aussi les styles Gothique et Windows XP, et plusieurs
palettes. Ils ont été retirés en version 7.0.0. Les préférences enregistrées ont été
migrées vers l'un des deux styles actuels ; les versions précédentes restent disponibles
sous forme de tags et sur la branche `legacy/6.x`.

## Tes données et ta vie privée

- Tout est enregistré sur ton ordinateur, dans `%LOCALAPPDATA%/AutoEldenRing/profiles-v3.json`.
  Sauvegarde ce fichier pour garder tout ton historique.
- Les enregistrements sont atomiques : un plantage ne peut pas laisser une bibliothèque à moitié écrite.
- Les fichiers de sauvegarde sont seulement lus, jamais copiés dans les données de
  l'application ni dans les releases.
- Les anciens formats sont mis à jour automatiquement ; personnages, objectifs, inventaire et
  chronologies sont conservés.
- Il n'y a ni code réseau, ni télémétrie, ni compte.

## Configuration requise

- Windows 10 ou 11, 64 bits. L'exécutable n'a besoin de rien d'autre.
- Pour lancer depuis les sources : Python 3.14 (64 bits) et les paquets de `requirements.txt`.

## Limites

- Windows uniquement.
- Le mode lecture peut tronquer quelques libellés courts de boutons, car leur largeur est fixe.
- Certaines traductions utilisent des pluriels génériques, comme « level(s) » ; les traductions
  autres que l'anglais n'ont pas été relues par des locuteurs natifs.
- Les tables de coûts sont les données fournies ; chaque entrée n'a pas été vérifiée en jeu.
- Les projections de farm sont des estimations, pas des garanties.
- L'application ne lit ni la mémoire du jeu en direct, ni la progression non sauvegardée.

## Mentions légales

Auto Elden Ring est un outil de fans non officiel. Il n'est ni affilié, ni approuvé, ni
sponsorisé par FromSoftware, Bandai Namco Entertainment ou leurs partenaires. *Elden Ring*,
ses noms et ses médias appartiennent à leurs ayants droit. Le code source est publié sous
[licence MIT](../LICENSE) ; cette licence ne couvre pas les médias du jeu. La provenance des
icônes et des noms est documentée dans [SOURCES.md](SOURCES.md).

## Documentation

- [Guide d'utilisation](GUIDE.md) — chaque écran et chaque parcours (en anglais).
- [Sources des données](SOURCES.md) — origine des tables de coûts, icônes et noms.
- [Journal des modifications](../CHANGELOG.md) — toutes les versions.
- [Releases](https://github.com/extrapirattaz/auto-elden-ring/releases) — téléchargements et sommes de contrôle.

# Données et règles — version 1.0.1

## Fichier fourni

`elden_ring_costs.json`, conservé byte pour byte : SHA-256 `3118f1c03fffaf832fdb453d6697d5da8b03007357333f2a2bec52f9b1e3a123`.

Ce fichier déclare la régulation 1.17.1 (11711000), 487 objets répartis dans 42 catégories, un maximum de personnage 713 et d'attribut 99. Il comprend 712 coûts de niveaux, 292 objets améliorables à +25, 194 à +10 et un bâton non améliorable. Les noms, catégories, indicateurs DLC et tarifs par passage proviennent de ce fichier. La présence d'une entrée de paramètres ne prouve pas sa disponibilité dans une édition du jeu.

Les métadonnées citent les projets suivants ; elles ne constituent pas une preuve de régénération indépendante de toute la table pendant ce travail :

- [Smithbox — régulations ER](https://github.com/vawser/Smithbox/tree/main/src/Smithbox.Data/Assets/PARAM/ER/Regulations)
- [Paramdex — définitions ER](https://github.com/soulsmods/Paramdex/tree/master/ER/Defs)
- [SaveForge — noms d'armes](https://github.com/oisis/EldenRing-SaveForge/tree/main/backend/db/data)
- [ERDB — armaments.py](https://github.com/EldenRingDatabase/erdb/blob/master/src/erdb/table/armaments.py)
- [Build advisor — méthode des niveaux](https://github.com/KCMO4/elden-ring-build-advisor/blob/main/AGENTS.md)

Le chargement contrôle la présence et la validité des coûts nécessaires. Les tests contrôlent toutes les transitions du catalogue ainsi que les 712 transitions de personnage contre la formule entière déclarée :

```python
cost_next_level = ((max(0, current_level - 11) * 2 + 10)
                   * (current_level + 81) ** 2) // 100 + 1
```

Le moteur additionne les tables exactes ; il n'utilise pas une formule flottante approximative pour produire les résultats. Du niveau 1 au niveau 713 : 1 692 566 842 runes selon la table fournie.

## Pierres et perles

Prix par défaut et déblocage consultés le 3 octobre 2026 dans [Resources — Elden Ring completion sheets](https://eldenring.redmaw.dev/sheets/resources), recoupés avec [Bell Bearing — Eldenpedia](https://eldenring.wiki.gg/wiki/Bell_Bearing) via ses résultats indexés.

- Normales [1–8] : 200, 400, 600, **900**, 1 200, 1 500, 2 400, 3 600 runes.
- Sombres [1–9] : 2 000, 3 000, 4 000, 6 000, 9 000, 12 000, 16 000, 20 000, 25 000 runes.
- Normales : 2, 4 puis 6 unités par palier, soit 12 de chaque jusqu'à +24.
- Sombres : une unité par amélioration jusqu'à +9.
- +25 normale / +10 sombre : une pierre de dragon ancienne adaptée ; pas d'achat infini avec les perles, prix par défaut inconnu.

Les prix modifiés par le joueur sont ses hypothèses. La disponibilité des sources limitées n'est pas automatisée. Aucune extraction de tous les `ShopLineupParam` des pierres n'a été réalisée dans cette session.

## Profils personnalisés et inverse

Les armes du catalogue utilisent leur propre table, y compris les arbalètes et balistes atypiques. Un profil standard normale calcule chaque passage avec le facteur `(5 + current_upgrade) / 5`. Le sombre standard utilise `(2 + current_upgrade) / 2` pour +1 à +9, puis ×6 pour +10. L'arrondi est effectué avec des fractions exactes et la méthode ties-to-even de `round`, correspondant à la méthode ERDB déclarée par le JSON.

Ces profils ne sont pas universels. La `Soldier's Crossbow`, la `Pulley Crossbow`, la `Jar Cannon` et d'autres entrées du catalogue montrent pourquoi le prix de base seul ne suffit pas pour toutes les armes. Le calcul inverse retourne les bases compatibles avec le profil choisi et les correspondances exactes du catalogue, sans conclure à une identification certaine.

## Classes et farm

Les dix classes et leurs huit attributs de départ sont ceux du fichier Python `classes_data.py` fourni. Le test vérifie leur relation `sum(attributes) - 79 == level` et que toutes atteignent 713 avec huit attributs à 99. Les classes d'autres éditions ne sont pas ajoutées sans données correspondantes.

Le farm utilise la différence réelle de runes saisie par le joueur, divisée par la durée et ajustée par son rendement soutenu. Les buffs sont uniquement une annotation. Le [Silver-Pickled Fowl Foot](https://eldenring.wiki.gg/wiki/Silver-Pickled_Fowl_Foot) et la [découverte d'objets](https://eldenring.wiki.gg/wiki/Discovery) concernent les objets ; le [Gold-Pickled Fowl Foot](https://www.gamerguides.com/elden-ring/database/items/consumables) concerne les runes. L'application ne simule ni la durée des buffs ni leur empilement.

## Outils similaires

[Tarnished.dev](https://www.tarnished.dev/) propose déjà des calculateurs de builds, d'armes, d'armures et de dégâts. L'idée d'un calculateur Elden Ring existe donc déjà. Auto Elden Ring vise ici une application Python hors ligne orientée coûts de runes, panier de matériaux et farm ; cette recherche ne garantit pas l'unicité du nom ou de la combinaison de fonctions.

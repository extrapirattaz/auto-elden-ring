# Vérification Auto Elden Ring 1.0.1

Les statuts ci-dessous distinguent les tests de l'application et la validation dans le jeu. Le rapport de l'EXE et les empreintes sont associés à la release dans `releases/1.0.1/`.

| Vérification | Statut / portée |
| --- | --- |
| Tables de niveau | PASS : 712 passages, formule entière déclarée, limites 1/713 et total niveau 1 → 713 |
| Classes | PASS : dix minima, huit attributs, limite 99 et niveau maximal |
| Catalogue | PASS : chargement des 487 entrées et paiement de chaque passage de forge conservé |
| Pierres | PASS : quantités, prix, partage du stock, perles, pierres de dragon distinctes |
| Budgets et inverse | PASS : bornes exactes, observation sur un passage ou une plage, profil standard et prix particuliers du catalogue |
| Farm | PASS : débit mesuré, arrondi supérieur du temps, runes en poche et rendement soutenu |
| Interface Python | PASS : vrais widgets Tk, catalogue → panier → farm, attributs, inverse, projets et CSV |
| Chronomètre | PASS : démarrage, arrêt, durée retenue et callback de fin ; le test automatisé force aussi l'échéance pour vérifier la fin sans attendre |
| EXE empaqueté | Rapport `VERIFICATION_EXE.json` produit par le binaire lui-même, données incluses et version identique |
| Dans le jeu | NOT TESTED : aucun passage de forge ou achat effectué dans Elden Ring pendant la vérification |
| Données de régulation | Provenance déclarée par le JSON fourni ; extraction indépendante des 487 armes non exécutée |
| GitHub | NOT TESTED : dépôt et publication réservés au propriétaire ; workflow fourni mais non exécuté sur GitHub |
| Autres PC | NOT TESTED : pas de matrice de machines Windows ou d'installation Windows vierge |

Commandes reproductibles :

```powershell
py -3 -m unittest discover -s tests -v
py -3 main.py --self-test
.\Auto-Elden-Ring-1.0.1-win-x64.exe --self-test --report .\verification.json
```

Les tests de forge contrôlent l'utilisation des tables, pas leur exactitude historique contre une extraction indépendante. Les captures dans `docs/screenshots/` montrent l'interface exécutée sur cette machine. Le manifeste de release associe les hashes de toutes les sources incluses au binaire correspondant.

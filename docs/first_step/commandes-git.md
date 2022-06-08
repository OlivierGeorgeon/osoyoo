# Liste commandes utiles pour git

## Créer une nouvelle branche

1. Création branche d'une nouvelle fonctionnalité sur une nouvelle branche
```git
git checkout -b ma_branche
```

2. Pousser la branche locale sur le dépôt distant
```git
git push origin ma_branche
```

3. Récupérer la branche distante sur ma machine en locale
```git
git fetch origin ma_branche
```

4. Une fois la branche merge sur "dev" on peut la supprimer
```
// Suppression en local
git branch -d localBranchName

// Suppression à distance
git push origin --delete remoteBranchName
```

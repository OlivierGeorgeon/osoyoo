# Etapes suivies afin de résoudre un problème empêchant l'installation des packages 

## Vérification de la compatibilité avec version de Python

Les packages utilisés dans ce projet sont tous compatibles avec Python 3.10.
Certains sont compatibles avec des versions de python supérieur à 3.8 et inférieur à 3.11.

## Fresh intallation

Suppression de python de l'ordinateur et reinstallation de python 3.10.
Vérification de l'installation correcte des fichiers dans le dossier Scripts.
Absence de certains fichiers, cela veut dire que l'installation est incomplète.

## Troubleshoot

On s'aperçoit que l'antivirus empêche la bonne installation de certains packets de python dont pip, nécessaire pour installer des packets.
Pip est donc installé "en parti", il est donc "cassé"/"incomplet".


## Réinstallation manuelle de pip

On vérifie si pip et python sont déjà installés:

````commandline
python
pip help
````
On installe pip sur Windows:
````commandline
python get-pip.py
````

On vérifie l'installation de pip et sa version

````commandline
pip -V
````

## Installation des packages

````commandline
pip install -r requirements.txt
````


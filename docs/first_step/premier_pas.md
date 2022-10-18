# Etape à réaliser pour utiliser le répo

## Etape 0: Intaller Pyton 10

S'il n'est pas déjà installé, intaller Python 3.10 depuis https://www.python.org/downloads/

Dans les préférences de Pycharm, ajouter le Python interpreter: Pyton 3.10.

## Etape 1: Les dépendances python 

Intaller les modules Python qui sont importés dans le projet. 
Cliquer sur les modules marqués en erreur et faire "Import module"

On peut tout installer d'un coupe avec le script suivant depuis le terminal :
```shell
pip3 install -r ./docs/first_step/requirements.txt
```

## Etape 2: Les dépendances Arduino

Pour installer les dépendances Arduino, installer les bibliotheques suivantes :

Installer la bibliotheque "servo" via le gestionnaire de biblioltheque de Arduino.
Telecharger en ligne et Installer les bibliotheques suivantes dans /Document/arduino/librairies :
[HMC5883L](https://github.com/jarzebski/Arduino-HMC5883L) - [Arduino_JSON](https://github.com/arduino-libraries/Arduino_JSON) - [WifiEsp](https://osoyoo.com/driver/mecanum_metal_chassis/for_mega2560/WiFiEsp-master.zip) - [MPU6050_L](https://www.arduino.cc/reference/en/libraries/mpu6050_light/).

La librairie [MPU6050](https://github.com/jarzebski/Arduino-MPU6050.git) est aussi utilisée mais il n'est pas nécessaire de l'installer car nous l'avons incluse dans le répertoire
`autocat_enacter/src/lib` après quelques modification.

```
void setAngleZ(float value) {angleZ = value;};
```

Il faut éditer MPU6050.cpp pour que la méthode begin ne revoie pas false si l'adresse n'est pas 0x68. Ligne 58:
```
fastRegister8(MPU6050_REG_WHO_AM_I);
```

La carte GY521 ne contient pas de compass. 
La carte GY-86 contient un compass mais la mesure du compass semble fausser la mesure du yaw.

Dans l'IDE Arduino, menu tools, sélectionner Board: `Ardunio Mega or Mega 2560` et Processor: `ATmega2560 (mega2560)`

Compiler le sketch `osoyoo_car_enacter.ino`.

(Si erreur de compliation "Serial1 is undefined in this scope", alors vérifier que vous compilez bien pour la bonne carte)

## Etape 3: L'initialisation du robot

Téléverser le script principal `autocat_enacter.ino` (via l'IDE Arduino) dans le robot.

## Etape 4: La connexion au robot

Vous devez créer un fichier `arduino_secrets.h` qui contient les paramètres wifi du robot. 

Placez-le dans le répartoire `autocat_enacter`, à coté du fichier `autocat_enacter.ino`.

Vous avez le choix entre deux modes de connexion:

### Connexion au robot par le routeur (préféré):

`arduino_secrets.h` contient: 

```
#define SECRET_WIFI_TYPE "STA"
#define SECRET_SSID "<your wifi SSID>"
#define SECRET_PASS "<your password>"
```

### Connexion direct au robot :

`arduino_secrets.h` contient: 

```
#define SECRET_WIFI_TYPE "AP"
```

## Etape 5: Utiliser le robot

Lancer le script python main.py.
#### Commandes de éplacements et d'action : 
    - Avancer = 8
    - Reculer = 2
    - Tourner a Gauche = 1
    - Tourner a Droite = 3
    - Arret = 5
    - Avancer jusqu'a une ligne noir = 0
    - Scan = '-'

####  Interagir avec la fenêtre Egocentrique
    - Click: select an interaction
    - Insert: Insérer un phénomène
    - Suppr: Supprimer une interaction ou un phénomène

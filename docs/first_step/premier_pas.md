# Etape à réaliser pour utiliser le répo

## Etape 0: Les dépendances (important a installer)

###Pour installer les dépendances python, faire la commande :
```shell
pip install -r ./docs/first_step/requirements.txt
```

###Pour installer les dépendances Arduino  , installer les bibliotheques suivantes :
Installer la bibliotheque "servo" via le gestionnaire de biblioltheque de Arduino.
Telecharger en ligne et Installer les bibliotheques suivantes dans /Document/arduino/librairies :
[HMC5883L](https://github.com/jarzebski/Arduino-HMC5883L) - [Arduino_JSON](https://github.com/arduino-libraries/Arduino_JSON) - [WifiEsp](https://osoyoo.com/driver/mecanum_metal_chassis/for_mega2560/WiFiEsp-master.zip) - [MPU6050_L](https://www.arduino.cc/reference/en/libraries/mpu6050_light/) - [MPU6050](https://github.com/jarzebski/Arduino-MPU6050.git)

Il faut créer la fonction setAngleZ dans la librairie MPU6050_light.h. En ligne 91, inserer :
```
void setAngleZ(float value) {angleZ = value;};
```

Il faut éditer MPU6050.cpp pour que la méthode begin ne revoie pas false si l'adresse n'est pas 0x68. Ligne 58:
```
fastRegister8(MPU6050_REG_WHO_AM_I);
```


La carte GY521 ne contient pas de compass. 
La carte GY-86 contient un compass mais la mesure du compass semble fausser la mesure du yaw.

## Etape 1: L'initialisation du robot

Téléverser le script principal Osoyoo_car_enacter.ino (via le logiciel arduino) dans le robot qui contient :
  * Initialisation du réseaux Wifi
  * La liste des caractères UTF-8 associées au fonction de déplacement

## Etape 2: La connexion au robot
Pour ce connecter au robot il y a 2 solutions. La premiere est par la connexion direct au robot et la seconde est via un routeur.

### Connexion direct au robot :
D'abord il faut mettre la lettre "W" a la ligne 17 dans le fichier 'Osoyoo_car_enacter.ino'. 
Puis il faut ce connecter au Wifi du robot pour pouvoir lui envoyer des paquets par le Wifi. Pour cela il faut allez dans le fichier EgoMemoryWindows.py et a la ligne 220 changer l'ip par celle du robot (récuperable a l'aide du moniteur dans Arduino).
Et pour finir le pc doit etre connecté au wifi du robot et normalement le pc est connecté au robot.

### Connexion au robot par le routeur :
Pour pouvoir connecter le robot et son pc au routeur il faut deja avoir un routeur d'allumé.
Ensuite il faut mettre la lettre "R" a la ligne 17 dans le fichier 'Osoyoo_car_enacter.ino'.
Puis il faut changer l'ip dans le fichier EgoMemoryWindows.py et a la ligne 220 changer l'ip par celle du robot (récuperable a l'aide du moniteur dans Arduino).
Et pour finir le pc doit etre connecté au routeur et normalement le pc est connecté au robot.

## Etape 3: Utiliser le robot

Lancer le script python main.py.
#### Touches de déplacements et d'action : 
    -Avancer = 8
    -Reculer = 2
    -Tourner a Gauche = 1
    -Tourner a Droite = 3
    -Arret = 5
    -Avancer jusqu'a une ligne noir = 0
    -Scan = '-'
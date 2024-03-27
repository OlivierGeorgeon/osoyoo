# Setup the environment

## Install Pycharm

From https://www.jetbrains.com/pycharm/

I am using Pycharm to develop the python program as well as the Arduino program.
To associate C/C++ syntax highlighting with `.ino` files, follow [Sawyer McLane's tutoral](https://samclane.dev/Pycharm-Arduino/). 

## Clone the project 

You can clone the project directly from within Pycharm as explained in [Pycharm documentation](https://www.jetbrains.com/help/pycharm/manage-projects-hosted-on-github.html#clone-from-GitHub). 

Github address: https://github.com/OlivierGeorgeon/osoyoo.git

## Install the required packages

After cloning the project, PyCharm may automatically propose you to install the required packages. 
Or you can execute this command in the project directory: 

```
pip install -r requirements.txt
```

# Setup the Arduino IDE

If you are editing your Arduino project in another IDE like Pycharm, then check "Use an external editor" in the Arduino IDE preferences.

## Install the Arduino libraries

This project uses the following libraries: 

|Library| Function | Where to find it |
|---|---|---|
|Servo  | Servo motor  | Installed by default with the Arduino IDE|
|HC-SR04| Ultrasonic telemeter| Regular Osoyoo robot|
|WifiEsp-master| Wifi Shield | Regular Osoyoo robot ([Lesson 5](https://osoyoo.com/2019/11/08/omni-direction-mecanum-wheel-robot-car-kit-v1-lesson-5-wifi-control-robot-car/)  : [WiFiEsp-master.zip](https://osoyoo.com/driver/mecanum_metal_chassis/for_mega2560/WiFiEsp-master.zip))|
|Arduino_JSON | JSON  | Arduino IDE Library manager|
|MPU6050 | Inertial Measurement Unit | Included in our project repository |
|HLC5883L | Compass | [jarzebski github](https://github.com/jarzebski/Arduino-HMC5883L) |
|MMC5883 | Compass |  Included in our project repository |
|Adafruit_TCS34725| Color sensor | Arduino IDE Library manager |

Follow the [Osoyoo introduction lessons](https://osoyoo.com/2019/11/08/omni-direction-mecanum-wheel-robotic-kit-v1/) to install the libraries needed by the regular Osoyoo Robot:  

## Information about these libraries

### MPU6050 

I adapted the [MPU6050 library by Korneliusz Jarzebski](https://github.com/jarzebski/Arduino-MPU6050) and included it in this project. 
I had to add a timeout to avoid freezing the main loop if the MPU6050 is not responding. This seems to happen because of the noise caused by the motors. 
In file `MPU6050.cpp`, I added this line after Wire.begin() in line 38 (documentation [here](https://github.com/arduino/ArduinoCore-avr/blob/master/libraries/Wire/src/Wire.cpp#L90)): 
```
Wire.setWireTimeout( 25000, true);
```

Also, I had to edit the `MPU6050.cpp` to prevent it from aborting the initialization process when the address is not 0x68:

![image](C:\Users\assi.karim\Desktop\imageswiki/MPU6050.png)

Figure 2: Comment the return false; in line 56

After looking at a few alternatives, I chose this library because it was also provided with my [Arduino kit by Elegoo](https://www.elegoo.com/collections/mega-2560-starter-kits/products/elegoo-mega-2560-the-most-complete-starter-kit).
It is provided in the [arduino-kits-support-files](https://www.elegoo.com/pages/arduino-kits-support-files). The file 
[Mega_2560_The_Most_Complete_Starter_Kit](http://69.195.111.207/tutorial-download/?t=Mega_2560_The_Most_Complete_Starter_Kit) contains the whole pedagogical material, including the electronic wiring diagram. 


### Arduino_JSON

Install Arduino_JSON by Arduino from the library manager:
![image](C:\Users\assi.karim\Desktop\imageswiki/arduinojson.png)
Don't mistake it with the library `ArduinoJSON` by Benoit Blanchon.

### HMC5883L

This library handles the compass chip HMC5883L implemented in some of the GY-86 imu cards,
It is available at https://github.com/jarzebski/Arduino-HMC5883L.

![image](C:\Users\assi.karim\Desktop\imageswiki/HMC5883L.jpg)
Figure 3: The IMU card with the compass chip labeled `L883/2131`.

If your compass chip begins with `L883`, include the following lines in `robot_define.h` for your robot:

```
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1
```

### MMC5883L

This library handles the compass chip Duinotech MMC5883L implemented in some imu cards. 
I followed the [article by David Such](https://reefwing.medium.com/connecting-the-duinotech-3-axis-compass-to-an-arduino-b13c28d7d936) that lists the different compass chips. 
I adapted this library from [his repo](https://github.com/Reefwing-Software/MMC5883MA-Arduino-Library). 

![image](C:\Users\assi.karim\Desktop\imageswiki/MMC5883L.jpg)
Figure 4: The IMU card with the compass chip labeled `5883/601X`.

If your compass chip begins with `5883`, include the following lines in `robot_define.h` for your robot:

```
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
```

# Local parameters

## Wifi 

In the `autocat_enacter\src\wifi` folder, next to the `WifiCat.cpp` and `WifiCat.h` files, create the file `arduino_secrets.h`.

This file is registered in [.gitignore](https://github.com/OlivierGeorgeon/osoyoo/blob/master/.gitignore) so it won't be pushed to GitHub. Your wifi password won't be shared to the world. 

To let the robot connect to your own wifi as a station (STA), `arduino_secrets.h` must contain:

```
#define SECRET_WIFI_TYPE "STA"
#define SECRET_SSID "<your wifi SSID>"
#define SECRET_PASS "<your password>"
```

Alternatively, to let the robot provide its own wifi `osoyoo_robot` as an access point (AP),  `arduino_secrets.h` must contain:

```
#define SECRET_WIFI_TYPE "AP"
```
The robot's IP address will show in the serial terminal: 

![image](C:\Users\assi.karim\Desktop\imageswiki/serialterminal.png)

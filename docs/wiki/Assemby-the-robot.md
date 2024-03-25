# Assembly the robot

Follow the instructions provided by OSOYOO: 
* [Model 1](https://osoyoo.com/2019/11/08/omni-direction-mecanum-wheel-robotic-kit-v1/)
* [Model 2](https://osoyoo.com/2022/07/05/v2-metal-mecanum-wheel-robotic-lesson1-robot-car-assembly-model-2021006600/)

## Optionally change the servo

The servo `LACC200610` provided by Osoyoo was jittering when the wheels were moving. I replaced it with the `SG90` servo from my Elegoo kit, which solved the problem.


# Modify some wiring

We have modified some wiring from the original osoyoo robot as listed in Table 1.

Table 1: Wiring modification
|Original |Modified ||
|---|---|---|
|5|23| Rear  Right Motor direction pin 1|
|6|25| Rear  Right Motor direction pin 2|
|13|6|Head servo pin|

Pins 5 and 6 were moved to 23 and 25 because they don't need the PWM functionality. These pins are declared in the file `Wheel.h`.

Pin 13 was moved to pin 6 to avoid the head jittering when downloading the sketch. This pin is declared in the file `Robot_define.h`.

# Connect the IMU card

Connect the IMU card to the wifi Shield following Table 2 and Figure 1. 
Note that the calibration offset varies significantly depending on the position of the card on the robot. 

Table 2: IMU Wiring
|GY-86 Imu|MEGA2560 Wifi Shield|
|---|---|
|Vcc|3v3|
|GND|GND|
|SCL|SCL|
|SDA|SDA|

![HMC5883L_wiring](https://github.com/OlivierGeorgeon/osoyoo/assets/11695651/ad768966-af8f-4bb0-853d-4555f6dd5da5)
Figure 1: wiring of GY-86 imu

# Connect the color sensor

Use the "long" two-hole version of the TCS34725. It has two LEDs, and the holes miraculously match holes on the robot platform (Figure 4).
Wire it to the Arduino MEGA according to Table 2. 
Use PINs 20 and 21 for SDA and SCL because the other SDA and SCL PINs are used for the IMU. They are the same. 
For the power line, I used the 3v yellow PINs on the Wifi Shield. 
Alternatively, the VIN PIN can be connected to a 5V PIN (red).

![IMG_8115](https://user-images.githubusercontent.com/11695651/229270982-c6d02f3a-db68-4b3a-a110-0910c88de84a.JPG)
Figure 4: TCS34725 color sensor mounted on two 40 mm pillars between the front wheel motors

![IMG_8111](https://user-images.githubusercontent.com/11695651/229271282-8f59b321-83d1-41a0-b1b4-20df9120ef7a.JPG)
Figure 5: TCS34725 color sensor to Arduino MEGA wiring

Table 2: PIN connection
|TCS34725 |MEGA2560 ||
|---|---|---|
|3v3|3v| On the Wifi Shield, yellow slots|
|GND|GND| On the Wifi Shield, black|
|SDA|SDA 20| |
|SCL|SCL 21| |
|LED|53|Digital output|

More information on the [TCS34725 adafruit webpage](https://learn.adafruit.com/adafruit-color-sensors/overview).

# The emotion LED

Install a common cathode RGB LED as shown below. 

![rgb](https://github.com/OlivierGeorgeon/osoyoo/assets/11695651/c9c52a55-6352-4033-ab9d-d28f2acd3f0a)

Figure 5: RGB LED with flat side on the left. The cathode is the longest lead.

Table 3: RGB LED connections
|RGB LED | |MEGA2560 / Wifi shield|
|---|---|---|
|Blue|| 2 |
|Green|| 3 |
|GND|10kΩ resistor| GND |
|Red|| 5 |

![IMG_8684](https://github.com/OlivierGeorgeon/osoyoo/assets/11695651/e21755d3-1f04-483c-b324-0aba3f3e01e3)
Figure 6: The common cathode RGB LED on pins 2, 3, 5, and its cathode connected to the ground via a 10kΩ resistor. Flat side on the right.
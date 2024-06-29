# Troubleshooting

## The head servo is overheating

This may be because you left the servo head connected to Pin 13.
Please make sure you moved it to Pin 6 as explained in [Modify some wiring](Assemby-the-robot.md#modify-some-wiring).

Pin 13 is used to control the built-in LED of the Arduino board. 
The petitcat arduino code sends a fast on/off signal to Pin 13 to make the LED blink quickly to indicate that the robot is waiting for a wifi command. 
If Pin 13 is connected to the head servo, the servo won't move but will overheat. 

## The robot moves backward

In some versions of the Osoyoo robot, the wheel wiring is backward. 
You may invert the wheel wiring or set negative coefficients to wheels in `robot_define.h` like this:

```
#define REAR_RIGHT_WHEEL_COEF -1
#define REAR_LEFT_WHEEL_COEF -1
#define FRONT_RIGHT_WHEEL_COEF -1
#define FRONT_LEFT_WHEEL_COEF -1
```

## Bad detection of objects by the HC-SR04 ultrasonic module

Bad reception of echo signals may result in: 
- PetitCat often fails to detect object.
- The outcome packet often misses the `"echo_distance"` field.
- After a "Scan" interaction, the `"echos"` field of the outcome packet contains no or few values.  

This may be caused by a poor electrical connection of the HC-SR04 ultrasonic module. 
Please check and tighten its wiring according to the diagram in [Osoyoo Lesson 2](https://osoyoo.com/2022/07/05/v2-mecanum-wheel-metal-chassis-robotic-for-arduino-mega2560-lesson-2-obstacle-avoidance-robot/).
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

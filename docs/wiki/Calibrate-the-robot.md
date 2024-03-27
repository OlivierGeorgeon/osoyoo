,# Center the head

Place an object in front of the robot. Press `"-"` to remote control the robot to perform a scan and align its head towards the object.
Switch off the robot.
Tighten the head on the servo axis such that the angle between the head direction and the robot x axis correspond to the value `"head_angle"` in the `outcome` packet (Figure 2). Positive angles correspond to the robot looking to the left (trigonometric direction). `0` is centered. 

# Calibrate the floor luminosity sensors

Follow instructions in [Lesson 3](https://osoyoo.com/2022/07/05/v2-metal-chassis-mecanum-wheel-robotic-for-arduino-mega2560-lesson3-5-point-line-tracking/). The adjustment of the potentiometer can be quite sensitive. It may be helpful to place the robot on shims to raise it by a few millimeters to prevent it from moving when it detects the black line.

# Calibrate the floor color sensor

Place the robot on a white sheet of paper. 
Press `"-"` to remote control the robot to perform a scan while staying in place. 
In `RobotDefine.h`, set the values of `WHITE_RED`, `WHITE_GREEN`, and `WHITE_BLUE` respectively to the values of `"red"`, `"green"`, and `"blue"` in the `outcome` packet read in the terminal.

# Calibrate the compass

The Body Memory Window (Figure 1) shows the compass points representing where the robot believed the south was at each of the last 10 steps. 
Large blue squares are compass points relative to the robot's orientation. 
As the robot turns around, they draw a circle around the robot. The better this circle is centered on the robot, the better the compass is calibrated. 
Small blue squares are compass points in an absolute position. The closest they are to each other, the better the compass and the gyroscope are calibrated.

![image](C:\Users\assi.karim\Desktop\imageswiki/bodymemoryview.png)

_Figure 1: Body Memory View. Large blue squares forming a circle: estimated positions of the south on each step relative to the robot's orientation. Small blue squares at the bottom: estimated positions of the south on each step in absolute position._

To calibrate the compass, remote control the robot to make it turn at least 8 times of 45°.

If you can see the circle of blue squares (you may need to zoom out) in Body Memory Window: 
* Select the Body Memory window and press `"O"`. This will center the circle of compass points and display the message `Compass offset adjusted by (x, y)` at the bottom of the window.  
* Add `"x"` to `COMPASS_X_OFFSET` and `"y"` to `COMPASS_Y_OFFSET` in `Robot_define.h`.
* Download the Arduino code to the robot and relaunch the PC application.

If you cannot see the circle of blue squares in Body Memory Window, or if pressing `O` returns an error message, then it means that the offset is too far off.
* Use the values of `"compass_x"` and `"compass_y"` (Figure 2) in the `Outcome` packet as initial values of `COMPASS_X_OFFSET` and `COMPASS_Y_OFFSET`, and redo the procedure

# Check the gyroscope calibration

The file `Robot_define.h` contains a parameter `GYRO_COEF` used to scale the gyroscope measure. 
Good news: the value `1` seems to work for all robots, no need to calibrate!

The PC application computes the azimuth of the robot as the average between (1) the azimuth measured by the compass and (2) the estimated azimuth obtained by adding the yaw measured by the gyroscope to the previous azimuth. 
The Body Memory window displays the delta between these two values. 
On average, we observe a difference on the order of 1 or 2 degrees, which is fine.  

# Calibrate the linear accelerometer

We use the linear accelerometer to detect impacts with obstacles. 
Figure 2 shows an example `Outcome` packet received by the PC from the robot. 
The non-nul `impact` field indicates that the robot detected an impact.

![image](C:\Users\assi.karim\Desktop\imageswiki/terminalwindow.png)

_Figure 2: The Terminal window in PyCharm. The outcome packet contains the fields `impact`, `max_x_acc`, and `min_x_acc` used to calibrate the accelerometer._

## Calibrate the linear accelerometer offset

To calibrate the linear accelerometer `x offset`:
* Place the robot on shims so that the wheels don't touch the floor and the robot won't move. Make sure it is horizontal to prevent the gravitational acceleration to affect the x acceleration measure.
* Press `8` and `2` to remote control the robot to move forward and backward several times. Since it can't move, the robot may stop immediately because it believes that it is blocked by an obstacle. 
* In the terminal, find the `max_x_acc` and `min_x_acc` in the `Outcome` packet. 
The `min_x_acc` should be negative and corresponds to a maximum backwards acceleration. 
* Add `(max_x_acc + min_x_acc)/2` to `ACCELERATION_X_OFFSET` in `Robot_define.h`. 
For example, with the values obtained in Figure 2, the value `(-46-66)/2=-56` must be added to `ACCELERATION_X_OFFSET`.
Compute the average over several steps. 
Try to obtain an offset value error better than +/-30.

Proceed similarly to calibrate the linear accelerometer `y offset`. 
Download the Arduino code to the robot.

## Calibrate the impact threshold

The accelerometer x impact threshold is the threshold of deceleration beyond which an impact outcome is triggered. 
To calibrate this threshold:
* Remote control the robot to move forward and backward and to bump into an obstacle.
* In the Terminal window, find the `max_x_acc` and `min_x_acc` in the `Outcome` packet. 
Now these values incorporate the offset defined previously.
* When the robot bumps into an obstacle while moving forward, the strong deceleration causes `min_x_acc` to have a high negative value. 
The `impact` outcome is triggered when `min_x_acc < -ACCELERATION_X_IMPACT_THRESHOLD`.
* When the robot bumps into an obstacle while moving backward, the strong deceleration causes `max_x_acc` to have a high positive value. 
The `impact` outcome is triggered when `max_x_acc > ACCELERATION_X_IMPACT_THRESHOLD`.
* In `Robot_define.h` increase `ACCELERATION_X_IMPACT_THRESHOLD` if the `impact` outcome is triggered when there is no impact. Decrease it if the `impact` outcome is not triggered when there is an impact.

Proceed similarly for the accelerometer y impact threshold.
Download the Arduino code to the robot.

## Calibrate the accelerometer x block threshold

The accelerometer x block threshold is the threshold beneath which the impact outcome is triggered if the robot cannot accelerate because it is blocked by an obstacle. To calibrate this threshold:
* Place the robot against an obstacle.
* Remote control the robot to try to move forward.
* In the Terminal window, find the `max_x_acc` and `min_x_acc` in the `Outcome` packet. 
* When the robot tries to move forward but is blocked by an obstacle, the x acceleration will remain low. 
The `impact` outcome is triggered when `max_x_acc < ACCELERATION_X_BLOCK_THRESHOLD` during the initial 100 milliseconds.
* When the robot tries to move backward but is blocked by an obstacle, the x acceleration will remain at a low negative value. 
The `impact` outcome is triggered when `min_x_acc > -ACCELERATION_X_BLOCK_THRESHOLD` during the initial 100 milliseconds.
* In `Robot_define.h` increase `ACCELERATION_X_BLOCK_THRESHOLD` if the `impact` outcome is triggered when the robot is not blocked by an obstacle. Decrease it if the `impact` outcome is not triggered when the robot is blocked by an obstacle.

Proceed similarly for the accelerometer y block threshold.
Download the Arduino code to the robot.

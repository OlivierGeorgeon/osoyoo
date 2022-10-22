# Autocat

The Autocat project aims at controlling the 
[osoyoo robot car](https://osoyoo.com/2019/11/08/omni-direction-mecanum-wheel-robotic-kit-v1/) 
to generate life-like behaviors. 

## Repository architecture

```
.
├── autocat         # The python application
├── autocat_enacter # The arduino application
├── docs            # Documentation
├── main.py         # Run this program on your PC            
└── README.md       # This file. Read it all!
```

## Getting started

* Move file `docs/first_step/arduino_secrets.h` into folder `autocat_enacter/` and specify your wifi parameters in it. 
* Download file `autocat_enacter.ino` to the robot using the arduino IDE.
* Read the robot's IP address in the arduino IDE terminal.
* Run the python application (`main.py`) on your desktop, providing the robot's IP adress as an argument.

## Tuning

Specify the parameters of your robot in the files: 
* `autocat_enacter/Robot_define.h` 
* `autocat/Robot/RobotDefine.py`

## More information 

English: 
* https://github.com/OlivierGeorgeon/osoyoo/wiki

French:
* https://github.com/UCLy/INIT2/blob/master/docs/first_step/premier_pas.md
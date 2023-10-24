# Autocat

The Autocat project aims at controlling the 
[osoyoo robot car](https://osoyoo.myshopify.com/collections/robot-car/products/osoyoo-omni-directinal-mecanum-wheels-robot-car-kit-for-arduino-mega2560-metal-chassis-dc-speed-encoder-motor-robotic-diy-stem-remote-controlled-educational-mechanical-diy-coding-for-teens-adult?variant=31634199183471) 
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

* Move file `docs/first_step/arduino_secrets.h` into folder `autocat_enacter/src/wifi` and specify your wifi parameters in it. 
* Download file `autocat_enacter.ino` to the robot using the arduino IDE.
* Read the robot's IP address in the arduino IDE terminal.
* Configure your arena and the IP address of your robots in `autocat/Robot/RobotDefine.py`
* Run the `main.py` python application on your desktop with the name of your arena and of your robots as arguments. In our case `python.exe -m main PetiteIA 1`

## Tuning

Specify the parameters of your robot in the files: 
* `autocat_enacter/Robot_define.h` 
* `autocat/Robot/RobotDefine.py`

## More information 

English: 
* https://github.com/OlivierGeorgeon/osoyoo/wiki

French:
* https://github.com/UCLy/INIT2/blob/master/docs/first_step/premier_pas.md
# Autocat

The Autocat project aims at controlling the 
[osoyoo robot car](https://osoyoo.myshopify.com/collections/robot-car/products/osoyoo-omni-directinal-mecanum-wheels-robot-car-kit-for-arduino-mega2560-metal-chassis-dc-speed-encoder-motor-robotic-diy-stem-remote-controlled-educational-mechanical-diy-coding-for-teens-adult?variant=31634199183471) 
to generate life-like behaviors. 

## Repository architecture

```
.
├── autocat          # The python application
├── docs             # Documentation
├── petitcat_arduino # The arduino application
├── tests            # Test scripts
├── main.py          # Run this program on your PC            
└── README.md        # This file. Read it all!
```

## Getting started

* Clone the projet to your local machine.
* Move file `docs/first_step/arduino_secrets.h` into folder `peticat_arduino/src/wifi` and specify your wifi parameters in it. 
* Download file `petitcat_arduino.ino` to the robot using the arduino IDE.
* Read the robot's IP address in the arduino IDE terminal.
* Configure your arena and the IP address of your robots in `autocat/Robot/RobotDefine.py`
* Run the `main.py` python application on your desktop with the name of your arena and of your robots as arguments. For example: `python.exe -m main chezOlivier 1`

## Tuning

Specify the parameters of your robot in the files: 
* `petitcat_arduino/Robot_define.h` 
* `autocat/Robot/RobotDefine.py`

## More information 

English: 
* [The project's wiki](https://github.com/OlivierGeorgeon/osoyoo/wiki)
* [Howard Schneider's unboxing report](https://github.com/OlivierGeorgeon/osoyoo/blob/master/docs/overview/Part_1_Easy_to_Read_Overview.md)

French:
* [La documentation écrite par les étudiants](https://github.com/UCLy/INIT2/blob/master/docs/first_step/premier_pas.md)
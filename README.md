# PetitCat

The PetitCat project aims at generating life-like behaviors in robots.
It uses the PetitCat Robot, an extension of the [osoyoo robot car](https://osoyoo.myshopify.com/collections/robot-car/products/osoyoo-omni-directinal-mecanum-wheels-robot-car-kit-for-arduino-mega2560-metal-chassis-dc-speed-encoder-motor-robotic-diy-stem-remote-controlled-educational-mechanical-diy-coding-for-teens-adult?variant=31634199183471). 


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
* Move file [arduino_secrets.h](docs/first_step/arduino_secrets.h) into folder `peticat_arduino/src/wifi` and specify your wifi parameters in it. 
* Set default value `#define ROBOT_ID 0` or configure your robot's specifics in [Robot_define.h](petitcat_arduino/Robot_define.h).
* Download file [petitcat_arduino.ino](petitcat_arduino/petitcat_arduino.ino) to the robot using the arduino IDE.
* Read the robot's IP address in the arduino IDE terminal.
* Connect your PC to the same wifi as the robot
* Run [test_remote_control_robot.ipynb](tests/test_remote_control_robot.ipynb) or [test_remote_control_robot.py](tests/test_remote_control_robot.py) on your PC to test remote controlling the robot. 
* Configure your arena and the IP address of your robots in [RobotDefine.py](autocat/Robot/RobotDefine.py)
* Run the [main.py](main.py) python application on your PC with the name of your arena and of your robots as arguments. For example: `python -m main chezOlivier 1`



## Documentation 

Test documentation 
* [test_remote_control_robot.md](docs/tests/test_remote_control_robot.md) Helps you test the communication between your PC and your robot.

Full project documentation in English: 
* [The project's wiki](https://github.com/OlivierGeorgeon/osoyoo/wiki) Helps you assembly your robot, calibrate it, and run the project.
* [Howard Schneider's full tutorial](docs/overview/Part_1_Easy_to_Read_Overview.md) Step by step explanations for beginners. 
* [Youtube playlist](https://youtube.com/playlist?list=PLlSPp5EpW5vFb-ZMCr8m0dIOoKEQe9CIE&si=HachYRwgJR8I-BbH) Demonstrations of behaviors. 

French additional information:
* [La documentation écrite par les étudiants](docs/first_step/premier_pas.md)

## Related projects

* [Simon Gay's project](https://gaysimon.github.io/robot/robot_navigation_en.html) Simon added a Banana Pi and a binocular camera to study navigation.

## References

Georgeon, O. L., Lurie, D.,  Robertson, P. (2024). Artificial enactive inference in three-dimensional world. Cognitive Systems Research, 101234. [doi:10.1016/j.cogsys.2024.101234](https://authors.elsevier.com/a/1ivtO4xrDwYOWV)

<!---
(https://doi.org/10.1016/j.cogsys.2024.101234).
--->
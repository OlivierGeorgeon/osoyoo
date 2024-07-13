# The PetitCat Project

The PetitCat Project uses open source software combined with open source hardware to enable the Python code of an AI project to interface on a real-time basis via Wi-Fi with lower-level C/C++ compiled code of a robotic embodiment. 
It implements the low-level layers of a Brain-Inspired Cognitive Architecture (BICA) to generate autonomous behaviors.

The project has lower cost software and hardware requirements than robotic projects utilizing more formal frameworks such as ROS2. 
Of more importance, the PetitCat Project readily allows the researcher to customize the project to her/his research requirements, and involves a modest learning curve. 
While the PetitCat Project was initially created to allow symbol grounding, enaction, active inference, predictive coding, and developmental and constructivist learning, it is suitable for a wide range of people, from the student to the serious AI/AGI/BICA researcher.

![petitcat logo](docs/petitcat_padding.png)


## Repository architecture

```
.
├── autocat          # The python application
├── docs             # Documentation
├── petitcat_arduino # The arduino application
├── tests            # Test scripts
├── LICENSE          # License terms
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
* [The project's wiki](docs/wiki/home.md) Helps you assemble your robot, calibrate it, and run the project.
* [Howard Schneider's full tutorial](docs/overview/Part_1_Easy_to_Read_Overview.md) Step by step explanations for beginners and researchers alike. The documentation is intended to give any user a pleasant experience with the project regardless of how seriously they intend to make use of the project. An issue for many researchers in using GitHub software is that it more often fails to work (or work properly) mainly because the thousands of litte things in the heads of the developers are not made clear to the non-involved user. Here we have gone to the other extreme, to make sure that the hardware and software will work for any user, although the more advanced topics are geared towards researchers rather than students. We have paid much attention to the main causes of poor GitHub and other open source software usability: incomplete documentation, dependency issues, environment configuration, version mismatches, non-graceful error handling, permissions and access, network/connectivity issues, stability, indadequate testing, user prerequisite knowledge. Easy-to-read, guaranteed-to-work and inexpensive may surprise you in producing an example of a superhuman AGI with robotic embodiment.
* [Youtube playlist](https://youtube.com/playlist?list=PLlSPp5EpW5vFb-ZMCr8m0dIOoKEQe9CIE&si=HachYRwgJR8I-BbH) Demonstrations of behaviors. 

Publications
* [Publications](docs/wiki/publications.md)

French additional information:
* [La documentation écrite par les étudiants](docs/first_step/premier_pas.md)

## Related projects

* [Simon Gay's project](https://gaysimon.github.io/robot/robot_navigation_en.html) Simon added a Banana Pi and a binocular camera to study navigation.

## References

Georgeon, O. L., Lurie, D.,  Robertson, P. (2024). 
Artificial enactive inference in three-dimensional world. Cognitive Systems Research, 101234. [doi:10.1016/j.cogsys.2024.101234](https://doi.org/10.1016/j.cogsys.2024.101234).
([PDF](https://hal.science/hal-04587508)).

# License

Copyright 2024 AFPICL and CNRS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

This project provides open-source software designed for seamless integration with open-source hardware platforms such as Arduino, Raspberry Pi, and BeagleBone.

![open source hardware](openhardwarelogo.png)


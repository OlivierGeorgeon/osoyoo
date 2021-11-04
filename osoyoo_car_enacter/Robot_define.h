#define ROBOT_ID 0 // 0: robot Doll, 1: robot UCLy, 2: robot Olivier

#if ROBOT_ID == 1

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L false
#define ROBOT_WHEELS_REVERSED false

#warning "Compiling for UCLy's robot"

#elif ROBOT_ID == 2

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L true
#define ROBOT_WHEELS_REVERSED false

#warning "Compiling for Olivier's robot"

#else

#define ROBOT_HAS_MPU6050  false
#define ROBOT_HAS_HMC5883L false
#define ROBOT_WHEELS_REVERSED false

#warning "Compiling for Paul's robot"

#endif


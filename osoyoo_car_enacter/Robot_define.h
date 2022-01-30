#define ROBOT_ID 2 // 0: robot Doll, 1: robot UCLy, 2: robot Olivier

#if ROBOT_ID == 1

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1.2
#define TURN_SPOT_MAX_DURATION 1700
#define TURN_SPOT_ENDING_DELAY 500
#define TURN_SPOT_ENDING_ANGLE 15
#define X_ACCELERATION_OFFSET 5.3 // Below the offset means acceleration, above means deceleration
#define ROBOT_SERVO_PIN 4

#warning "Compiling for UCLy's robot"

#elif ROBOT_ID == 2

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L true
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1.1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 1700
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define X_ACCELERATION_OFFSET 5.3 // Below the offset means acceleration, above means deceleration
#define ROBOT_SERVO_PIN 4

#warning "Compiling for Olivier's robot"

#else

#define ROBOT_HAS_MPU6050  false
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 1300
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define X_ACCELERATION_OFFSET 5.3
#define ROBOT_SERVO_PIN 13

#warning "Compiling for Paul's robot"

#endif


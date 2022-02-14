#define ROBOT_ID 1 // 0: robot Doll, 1: robot UCLy, 2: robot Olivier

#if ROBOT_ID == 1

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1.2
#define TURN_SPOT_MAX_DURATION 1700
#define TURN_SPOT_ENDING_DELAY 500
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET -40
#define ACCELERATION_SHOCK_THRESHOLD -200
#define ACCELERATION_BLOCK_THRESHOLD 60  // TODO depends whether the interaction starts when the robot is immobile
#define GYRO_SHOCK_THRESHOLD 1 // °/s
#define ROBOT_SERVO_PIN 4  // 13 Changed because 13 is used for internal led

#warning "Compiling for UCLy's robot"

#elif ROBOT_ID == 2

#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L true
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1.1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 1700
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define COMPASS_X_OFFSET 1475
#define COMPASS_Y_OFFSET -1685
#define ACCELERATION_X_OFFSET 550 //
#define ACCELERATION_SHOCK_THRESHOLD -150 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_BLOCK_THRESHOLD 60 // Below the threshold, the robot is blocked
#define GYRO_SHOCK_THRESHOLD 1.5 // °/s Above the threshold is a shock to the left
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
#define ACCELERATION_X_OFFSET 530 // TODO set this value
#define ACCELERATION_SHOCK_THRESHOLD -200 // TODO set this value
#define ACCELERATION_BLOCK_THRESHOLD 30 // TODO set this value
#define GYRO_SHOCK_THRESHOLD 1 // °/s TODO set this value
#define ROBOT_SERVO_PIN 13

#warning "Compiling for Paul's robot"

#endif


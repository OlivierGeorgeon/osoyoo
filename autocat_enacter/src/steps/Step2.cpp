#include <Arduino_JSON.h>
#include "Step0.h"
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"

extern Wheel OWM;
extern Floor FCR;
extern Head HEA;
extern Imu IMU;
extern WifiCat WifiCat;
extern char packetBuffer[100];

extern unsigned long action_start_time;
extern unsigned long duration1;
extern unsigned long action_end_time;
extern int interaction_step;
extern char action;
extern String status; // The outcome information used for sequential learning
extern int robot_destination_angle;
extern int head_destination_angle;
extern int target_angle;
extern int target_duration;
extern bool is_focussed;
extern int focus_x;
extern int focus_y;
extern int focus_speed;
extern int clock;
extern int previous_clock;
extern int shock_event;


// Wait for the interaction to terminate and proceed to Step 3
// Warning: in some situations, the head alignment may take quite long
void Step2()
{
  if (action_end_time < millis() &&  !FCR._is_enacting && !HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
  {
    interaction_step = 3;
  }
}
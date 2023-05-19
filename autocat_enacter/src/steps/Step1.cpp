#include <Arduino_JSON.h>
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"

extern Wheel OWM;
extern Floor FCR;
extern Head HEA;
extern Imu IMU;

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
extern int target_focus_angle;
extern bool is_focussed;
extern int focus_x;
extern int focus_y;
extern int focus_speed;
extern int shock_event;


void Step1()
{
  switch (action)
  {
    case ACTION_GO_ADVANCE:
      if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
        HEA.turnHead(HEA.head_direction(focus_x - focus_speed * (millis()- action_start_time)/1000, focus_y));}
      if (shock_event > 0 && !FCR._is_enacting){
        // If shock then stop the go advance action
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        OWM.stopMotion();
        interaction_step = 2;
        break;
      }
      // Check if Floor Change Retreat
      if (FCR._is_enacting) {
        FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
        status ="1";
        // Proceed to step 2 for enacting Floor Change Retreat
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      // If no floor change, check whether duration has elapsed
      else if (action_end_time < millis()) {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
    case ACTION_GO_BACK:
      if (is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action)
        {HEA.turnHead(HEA.head_direction(focus_x + focus_speed * (millis()- action_start_time)/1000, focus_y));}
      // Check if Floor Change Retreat
      if (FCR._is_enacting) {
        FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
        status ="1";
        // Proceed to step 2 for enacting Floor Change Retreat
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      // If no floor change, check whether duration has elapsed
      else if (action_end_time < millis()) {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
    case ACTION_SHIFT_RIGHT:
      if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
        HEA.turnHead(HEA.head_direction(focus_x, focus_y + focus_speed * (millis()- action_start_time)/1000));}
      // Check if Floor Change Retreat
      if (FCR._is_enacting) {
        FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
        status ="1";
        // Proceed to step 2 for enacting Floor Change Retreat
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      // If no floor change, check whether duration has elapsed
      else if (action_end_time < millis()) {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
    case ACTION_SHIFT_LEFT:
      if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
        HEA.turnHead(HEA.head_direction(focus_x, focus_y - focus_speed * (millis()- action_start_time)/1000));}
      // Check if Floor Change Retreat
      if (FCR._is_enacting) {
        FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
        status ="1";
        // Proceed to step 2 for enacting Floor Change Retreat
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      // If no floor change, check whether duration has elapsed
      else if (action_end_time < millis()) {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
    case ACTION_TURN_RIGHT:
    case ACTION_TURN_LEFT:
      // Check if Floor Change Retreat
      if (FCR._is_enacting) {
        FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
        status ="1";
        // Proceed to step 2 for enacting Floor Change Retreat
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      // If no floor change, check whether duration has elapsed
      else if (action_end_time < millis()) {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
    case ACTION_TURN_IN_SPOT_LEFT:
      // Keep head aligned with destination angle
      if (is_focussed){
        //float current_robot_direction = (head_destination_angle - IMU._yaw) * M_PI / 180.0;
        float current_focus_direction = (target_focus_angle - IMU._yaw) * M_PI / 180.0; // relative to robot
        float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
        float current_head_direction = HEA.head_direction(cos(current_focus_direction) * r, sin(current_focus_direction) * r);
        // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
        HEA.turnHead(current_head_direction); // Keep looking at destination
      } else {
        HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
      }
       // Stop before reaching destination angle or when duration has elapsed
      if ((IMU._yaw > robot_destination_angle - TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
      {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
        action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
      }
      break;
    case ACTION_TURN_IN_SPOT_RIGHT:
      // Keep head aligned with destination angle
      if (is_focussed){
        // float current_robot_direction = (head_destination_angle - IMU._yaw) * M_PI / 180.0;
        float current_focus_direction = (target_focus_angle - IMU._yaw) * M_PI / 180.0;
        float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
        float current_head_direction = HEA.head_direction(cos(current_focus_direction) * r, sin(current_focus_direction) * r);
        // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
        HEA.turnHead(current_head_direction); // Keep looking at destination
      } else {
        HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
      }
      // Stop before reaching destination angle or when duration has elapsed
      if ((IMU._yaw < robot_destination_angle + TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
      {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
        action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
      }
      break;
    case ACTION_ALIGN_ROBOT:
      if (is_focussed){
        float current_robot_direction = (robot_destination_angle - IMU._yaw) * M_PI / 180.0;
        float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
        float current_head_direction = HEA.head_direction(cos(current_robot_direction) * r, sin(current_robot_direction) * r);
        // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
        HEA.turnHead(current_head_direction); // Keep looking at destination
      } else {
        HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
      }
      if (((robot_destination_angle > TURN_FRONT_ENDING_ANGLE) && (IMU._yaw > robot_destination_angle - TURN_FRONT_ENDING_ANGLE)) ||
      ((robot_destination_angle < -TURN_FRONT_ENDING_ANGLE) && (IMU._yaw < robot_destination_angle + TURN_FRONT_ENDING_ANGLE)) ||
      (abs(robot_destination_angle) < TURN_FRONT_ENDING_ANGLE))
      {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
        action_end_time = millis() + TURN_FRONT_ENDING_DELAY;// give it time to immobilize before terminating interaction
      }
      break;
    case ACTION_ALIGN_HEAD:
    /*case ACTION_ECHO_COMPLETE:
      if(!HECS._is_enacting_echo_scan){
        action_end_time = 0;
        interaction_step = 2;
      }
      break;*/
    case ACTION_SCAN_DIRECTION:
      if (!HEA._is_enacting_head_alignment && !HEA._is_enacting_echo_scan)
      {
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      break;
    case ACTION_ECHO_SCAN:
      if (!HEA._is_enacting_echo_scan)
      {
        if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
        duration1 = millis()- action_start_time;
        action_end_time = 0;
        interaction_step = 2;
      }
      break;
    default:
      if (action_end_time < millis()) {
        duration1 = millis()- action_start_time;
        OWM.stopMotion();
        interaction_step = 2;
      }
      break;
  }
}
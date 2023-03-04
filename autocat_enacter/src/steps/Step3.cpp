#include <Arduino_JSON.h>
#include "Step0.h"
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"

extern String status; // The outcome information used for sequential learning
extern char action;
extern int clock;
extern Floor FCR;
extern Head HEA;
extern Imu IMU;
extern unsigned long duration1;
extern unsigned long action_start_time;
extern int interaction_step;
extern WifiCat WifiCat;



// Wait for the interaction to terminate and proceed to Step 3
// Warning: in some situations, the head alignment may take quite long
void Step3()
{
  // Compute the outcome message
  JSONVar outcome_object;
  outcome_object["status"] = status;
  outcome_object["action"] = String(action);
  outcome_object["clock"] = clock;
  FCR.outcome(outcome_object);
  HEA.outcome(outcome_object);
  HEA.outcome_complete(outcome_object);
  IMU.outcome(outcome_object, action);

  // HECS.outcome(outcome_object);
  outcome_object["duration1"] = duration1;
  outcome_object["duration"] = millis() - action_start_time;

  // Send the outcome to the PC
  String outcome_json_string = JSON.stringify(outcome_object);
  digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
  WifiCat.send(outcome_json_string);
  digitalWrite(LED_BUILTIN, LOW);

  // Ready to begin a new interaction
  interaction_step = 0;
}
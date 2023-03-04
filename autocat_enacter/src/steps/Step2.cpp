#include <Arduino_JSON.h>
#include "Step0.h"
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"

extern Head HEA;
extern Floor FCR;
extern unsigned long action_end_time;
extern int interaction_step;


// Wait for the interaction to terminate and proceed to Step 3
// Warning: in some situations, the head alignment may take quite long
void Step2()
{
  if (action_end_time < millis() &&  !FCR._is_enacting && !HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
  {
    interaction_step = 3;
  }
}
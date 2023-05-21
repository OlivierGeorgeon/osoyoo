#include <Arduino_JSON.h>
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
//#include "../../Imu.h"

extern Color TCS;
extern Floor FCR;
extern Head HEA;
extern unsigned long action_end_time;
extern int interaction_step;


// Wait for the interaction to terminate and proceed to Step 3
// Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
// Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
// Warning: in some situations, the head alignment may take quite long
void Step2()
{
  if (action_end_time < millis() &&  !FCR._is_enacting && !HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
  //if (action_end_time < millis() &&  !FCR._is_enacting)
  {
    TCS.read();
    interaction_step = 3;
  }
}
#ifndef WifiBot_h
#define WifiBot_h
#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

class WifiBot
{
  public:
    // Constructor
    WifiBot(String _ssid, int port);

    // Variable
    WiFiEspUDP Udp;
    int status;
    unsigned int localPort;
    String ssid;

    /*
     * Method to connect wifi
     * Execute in robot setup fonction
     *
     * wifiInitLocal: connect with robot access point
     *  OR
     * wifiInitRouter: robot connect with router
     */
    void wifiInitLocal();
    void wifiInitRouter();

  /*
   * Method for print all wifi information of the robot (IP, Port, ...)
   */
    void printWifiStatus();
  
  /*
   * Method for send String by wifi
   * Example: sendOutcome(JsonOutcome.get()) for send json data convert to String
   */
    void sendOutcome(String json);
};

#endif
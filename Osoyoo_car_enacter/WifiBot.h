#ifndef WifiBot_h
#define WifiBot_h

#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

class WifiBot
{
  public:
    //Constructeur
    WifiBot();

    //Variable
    WiFiEspUDP Udp;
    int status;
    unsigned int localPort;
    String ssid;

    //Methode
    void wifiInit();

    void printWifiStatus();

    void sendOutcome(String json);
};

#endif
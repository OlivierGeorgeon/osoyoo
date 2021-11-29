#ifndef WifiBot_h
#define WifiBot_h
#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

class WifiBot
{
  public:
    //Constructeur
    WifiBot(String _ssid, int port);

    //Variable
    WiFiEspUDP Udp;
    int status;
    unsigned int localPort;
    String ssid;

    //Methode
    //void wifiInit();
    void wifiInitLocal();
    void wifiInitRouter();

    void printWifiStatus();

    void sendOutcome(String json);
};

#endif
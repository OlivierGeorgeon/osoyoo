/*
  WifiCat.h - library for Robot wifi control.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/
#ifndef WifiCat_h
#define WifiCat_h
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

class WifiCat
{
  public:
    WifiCat();
    // Initialize the wifi
    void begin();
    // Read the received UDP string
    int read(char* packetBuffer);
    // Send the outcome UDP string to the PC
    void send(String outcome_json_string);
  private:
    // The UDP object used to receive and send data
    WiFiEspUDP Udp;
};

#endif
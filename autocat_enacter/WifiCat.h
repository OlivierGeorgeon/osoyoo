/*
  WifiCat.h - library for Robot wifi control.
  Created by Celien Fiorelli, june 20 2021
  released into the public domain
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
    // The UDP object used to receive and send data
    WiFiEspUDP Udp;
  private:
};

#endif
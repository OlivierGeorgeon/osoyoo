/*
  WifiCat.h - library for Robot wifi control.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/
#ifndef WifiCat_h
#define WifiCat_h
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

#define WIFI_CHANNEL 10 // 10 was the original value in the Osoyoo demo
#define PORT 8888
#define UDP_BUFFER_SIZE 100 // If the received packet exceeds this size, Arduino may crash

class WifiCat
{
  public:
    WifiCat();
    // Initialize the wifi
    void begin();
    // Read the received UDP string
    int read(char* packetBuffer);
    // Send the outcome UDP string to the PC
    void send(String message);
  private:
    // The UDP object used to receive and send data
    WiFiEspUDP Udp;
};

#endif
/*
  WifiCat.cpp - library for Robot wifi control.
  Created by Celien Fiorelli, june 20 2021
  released into the public domain
*/
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

#include "WifiCat.h"
#include "arduino_secrets.h"
#include "Robot_define.h"

#define WIFI_CHANNEL 10 // 10 was the original value in the Osoyoo demo
#define PORT 8888

WifiCat::WifiCat()
{
}

// Initialize the wifi
void WifiCat::begin()
{
  // Connect to the wifi board
  Serial1.begin(115200);
  Serial1.write("AT+UART_DEF=9600,8,1,0,0\r\n");
  delay(200);
  Serial1.write("AT+RST\r\n");
  delay(200);
  Serial1.begin(9600);    // initialize serial for ESP module
  WiFi.init(&Serial1);    // initialize ESP module
  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }
  // Connect to the wifi network
  int status = WL_IDLE_STATUS;
  if (SECRET_WIFI_TYPE == "AP") { // Wifi parameters in arduino_secret.h
    // Connecting to wifi as an Access Point (AP)
    char ssid[] = AP_SSID;
    Serial.print("Attempting to start AP SSID: ");
    Serial.println(ssid);
    status = WiFi.beginAP(ssid, WIFI_CHANNEL, "", 0);
  } else {
    // Connecting to wifi as a Station (STA)
    char ssid[] = SECRET_SSID;
    char pass[] = SECRET_PASS;
    while (status != WL_CONNECTED) {
      Serial.print("Attempting to connect to WPA SSID: ");
      Serial.println(ssid);
      status = WiFi.begin(ssid, pass);
    }
  }
  Udp.begin(PORT);

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Listening on port: ");
  Serial.println(PORT);
}

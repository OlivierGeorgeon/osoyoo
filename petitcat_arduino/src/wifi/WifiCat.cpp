/*
  WifiCat.cpp - library for PetitCat robot wifi control.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

#include "WifiCat.h"
#include "arduino_secrets.h"
#include "../../Robot_define.h"

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
  if (WiFi.status() == WL_NO_SHIELD)
  {
    Serial.println("WiFi shield not present");
    // Block the robot
    while (true);
  }

  // Connect to the wifi network

  int status = WL_IDLE_STATUS;
  // Connection depends on the Wifi parameters in arduino_secret.h
  if (SECRET_WIFI_TYPE == "AP")
  {
    // Connecting to wifi as an Access Point (AP)
    char ssid[] = AP_SSID;
    Serial.print("Attempting to start AP SSID: ");
    Serial.println(ssid);
    status = WiFi.beginAP(ssid, WIFI_CHANNEL, "", 0);
  }
  else
  {
    // Connecting to wifi as a Station (STA)
    char ssid[] = SECRET_SSID;
    char pass[] = SECRET_PASS;
    while (status != WL_CONNECTED)
    {
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

// Read up tp 512 characters from the current packet and place them to the buffer
// Returns the number of bytes read, or 0 if none are available

int WifiCat::read(char* packetBuffer)
{
  int len = 0;
  if (Udp.parsePacket())
  {
    len = Udp.read(packetBuffer, UDP_BUFFER_SIZE - 1);
    packetBuffer[len] = 0;
    Serial.print("Income string: ");
    Serial.println(packetBuffer);
    Udp.flush(); // Discard any remaining input data. Test for debug

    //Serial.print("From ");
    //Serial.print(Udp.remoteIP());
    //Serial.print("/");
    //Serial.println(Udp.remotePort());
  }
  return len;
}

// Send the outcome to the IP address and port that sent the action

void WifiCat::send(String message)
{
  Serial.println("Outcome string: " + message);
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.print(message);
  // Udp.endPacket(); // does nothing: just returns 1
}

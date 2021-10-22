#include "WifiBot.h"

#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

WifiBot::WifiBot()
{
    localPort = 8888;
    status = WL_IDLE_STATUS;
    ssid = "osoyoo_robot2";
}

void WifiBot::wifiInit()
{
  Serial.begin(9600);
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

   Serial.print("Attempting to start AP ");
   String str = "This is my string";


    int str_len = ssid.length() + 1;
    char char_ssid[str_len];
    ssid.toCharArray(char_ssid, str_len);

   Serial.println(char_ssid);
   //AP mode
   status = WiFi.beginAP(char_ssid, 10, "", 0);

  Serial.println("You're connected to the network");
  printWifiStatus();
  Udp.begin(localPort);

  Serial.print("Listening on port ");
  Serial.println(localPort);
}

void WifiBot::printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print where to go in the browser
  Serial.println();
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
  Serial.println();
}

void WifiBot::sendOutcome(String json)
{
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.print(json);
  Udp.endPacket();
}
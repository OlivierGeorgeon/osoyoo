#include "WifiBot.h"
#include "WiFiEsp.h"
#include "WiFiEspUDP.h"
#define USER_ID "RobotBSN"
#define PASSWD "BSNgoodlife"
#define PORT "8888"
int status = WL_IDLE_STATUS;     // the Wifi radio's status

WifiBot::WifiBot(String _ssid, int port)
{
    localPort = port;
    status = WL_IDLE_STATUS;
    ssid = _ssid;
}

void WifiBot::wifiInitLocal()
{
  Serial1.begin(115200);
  Serial1.write("AT+UART_DEF=9600,8,1,0,0\r\n");
  delay(200);
  Serial1.write("AT+RST\r\n");
  delay(200);
  Serial1.begin(9600);    // initialize serial for ESP module
  WiFi.init(&Serial1);    // initialize ESP module
  //IPAddress ip = WiFi.localIP();

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
  //printWifiStatus();
  Udp.begin(localPort);

  Serial.print("Listening on port ");
  Serial.println(localPort);
}

void WifiBot::wifiInitRouter()
{

  // initialize serial for ESP module
  Serial1.begin(9600);
  // initialize ESP module
  WiFi.init(&Serial1);

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(USER_ID);
    // Connect to WPA/WPA2 network
    status = WiFi.begin(USER_ID, PASSWD);
  }

  Serial.println("You're connected to the network");
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  Udp.begin(localPort);
  Serial.print("Listening on port ");
  Serial.println(localPort);
}


void WifiBot::sendOutcome(String json)
{
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.print(json);
  Udp.endPacket();
}
/*
  StationHub ESP32 Standalone Web Server
  Creates an isolated Wi-Fi Access Point and serves the local PS5 host.
*/

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <SPIFFS.h>

const char* ssid = "PS5_HOST_AP";
const char* password = ""; // Open AP or set password

const byte DNS_PORT = 53;
IPAddress apIP(192, 168, 4, 1);
IPAddress netMsk(255, 255, 255, 0);

DNSServer dnsServer;
WebServer server(80);

void handleRoot() {
  File file = SPIFFS.open("/index.html", "r");
  if (!file) {
    server.send(200, "text/plain", "Host listo. Sube los archivos a SPIFFS.");
    return;
  }
  server.streamFile(file, "text/html");
  file.close();
}

void setup() {
  Serial.begin(115200);
  SPIFFS.begin(true);

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, netMsk);
  WiFi.softAP(ssid, password);

  // Redirect all DNS requests (Captive Portal)
  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", apIP);

  server.on("/", handleRoot);
  server.onNotFound([]() {
    handleRoot();
  });

  server.begin();
  Serial.println("ESP32 PS5 Server listo. Conectar a WiFi: PS5_HOST_AP");
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
}

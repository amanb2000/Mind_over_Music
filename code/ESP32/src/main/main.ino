/**
 * Muse BLE Client on ESP32
 */
#include <Arduino.h>
#include "BLEDevice.h"
#include <WiFi.h>
#include <WiFiUdp.h>
//#include "BLEScan.h"

// The remote service we wish to connect to.
static BLEUUID serviceUUID("0000fe8d-0000-1000-8000-00805f9b34fb");
// The characteristic of the remote service we are interested in.
static BLEUUID    presetHandler("273e0001-4c4d-454d-96be-f03bac821358");
static BLEUUID    streanHandler("273e0001-4c4d-454d-96be-f03bac821358");

static BLEUUID    charStreamUUID("273e0001-4c4d-454d-96be-f03bac821358");
static BLEUUID    charTP9UUID("273e0003-4c4d-454d-96be-f03bac821358");
static BLEUUID    charAF7UUID("273e0004-4c4d-454d-96be-f03bac821358");
static BLEUUID    charAF8UUID("273e0005-4c4d-454d-96be-f03bac821358");
static BLEUUID    charTP10UUID("273e0006-4c4d-454d-96be-f03bac821358");
static BLEUUID    charRightAuxUUID("273e0007-4c4d-454d-96be-f03bac821358");
static BLEUUID    charGyroUUID("273e0009-4c4d-454d-96be-f03bac821358");
static BLEUUID    charAccelerometerUUID("273e000a-4c4d-454d-96be-f03bac821358");
static BLEUUID    charTelemetryUUID("273e000b-4c4d-454d-96be-f03bac821358");

static BLEUUID    unknown1UUID("273e0008-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown2UUID("273e000c-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown3UUID("273e000d-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown4UUID("273e000e-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown5UUID("273e000f-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown6UUID("273e0010-4c4d-454d-96be-f03bac821358");
static BLEUUID    unknown7UUID("273e0011-4c4d-454d-96be-f03bac821358");

static bool doConnect = false;
static bool connected = false;
static bool doScan = true;
BLERemoteService* pRemoteService;
static BLERemoteCharacteristic* pRemoteCharacteristic;
static BLEAdvertisedDevice* myDevice;

// WiFi
const char * ssid = "Bird";
const char * pwd = "changeme";

/*const char * ssid = "Randy";
const char * pwd = "doinkboy";
*/
//const char * udpAddress = "172.20.10.4";
const char * udpAddress = "192.168.43.150";
const int udpPort = 9999;
WiFiUDP udp;

void sendUdp(uint16_t handle, uint8_t* packet, size_t length){
  udp.beginPacket(udpAddress, udpPort);
  udp.printf("%d",handle);
  udp.write(packet, length);
  udp.endPacket();
}

static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify) {
    Serial.printf("%d",pBLERemoteCharacteristic->getHandle());
    Serial.print(", length: ");
    Serial.println(length);
    Serial.print("data: ");
    Serial.println((char*)pData);
    sendUdp(pBLERemoteCharacteristic->getHandle(), pData, length);
}

class MyClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
  }

  void onDisconnect(BLEClient* pclient) {
    connected = false;
    doScan=true;
    Serial.println("onDisconnect");
  }
};

void subscribe() {
  pRemoteService->getCharacteristic(charTP9UUID)->registerForNotify(notifyCallback);

  pRemoteService->getCharacteristic(charAF7UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(charAF8UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(charTP10UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(charRightAuxUUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(charGyroUUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(charAccelerometerUUID)->registerForNotify(notifyCallback);
}

void subscribeUnknown() {
  pRemoteService->getCharacteristic(unknown1UUID)->registerForNotify(notifyCallback);

  pRemoteService->getCharacteristic(unknown2UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(unknown3UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(unknown4UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(unknown5UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(unknown6UUID)->registerForNotify(notifyCallback);
  
  pRemoteService->getCharacteristic(unknown7UUID)->registerForNotify(notifyCallback);
}


void connectToWiFi(){
   WiFi.begin(ssid, pwd);
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

bool connectToServer() {
    Serial.print("Forming a connection to ");
    Serial.println(myDevice->getAddress().toString().c_str());
    
    BLEClient*  pClient  = BLEDevice::createClient();
    Serial.println(" - Created client");

    pClient->setClientCallbacks(new MyClientCallback());

    // Connect to the remove BLE Server.
    pClient->connect(myDevice);  // if you pass BLEAdvertisedDevice instead of address, it will be recognized type of peer device address (public or private)
    Serial.println(" - Connected to server");

    // Obtain a reference to the service we are after in the remote BLE server.
    pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      Serial.print("Failed to find our service UUID: ");
      Serial.println(serviceUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our service");

    subscribe(); //listen to EEG and IMU
    //subscribeUnknown();

    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charStreamUUID);
    if (pRemoteCharacteristic == nullptr) {
      Serial.print("Failed to find our characteristic UUID: ");
      Serial.println(charStreamUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our characteristic");

    // Read the value of the characteristic.
    //if(pRemoteCharacteristic->canWrite()) {
      Serial.println("Will write to stream control");
      //const uint8_t data1[]={0x04, 0x50, 0x33, 0x31, 0x0a};
      const uint8_t data1[]={0x04, 0x70, 0x32, 0x30, 0x0a};
      size_t length1 = 5;
      pRemoteCharacteristic->writeValue((uint8_t*)data1, length1, false);

      const uint8_t data2[]={0x02, 0x64, 0x0a};
      size_t length2 = 3;
      pRemoteCharacteristic->writeValue((uint8_t*)data2, length2, false);
    //} else {
    //  Serial.println("Cannot write :(");
   // }

    if(pRemoteCharacteristic->canNotify())
      pRemoteCharacteristic->registerForNotify(notifyCallback);
    else Serial.println("Cannot notify :(");
connectToWiFi();
    connected = true;
    return connected;
}
/**
 * Scan for BLE servers and find the first one that advertises the service we are looking for.
 */
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
 /**
   * Called for each advertising BLE server.
   */
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.print("BLE Advertised Device found: ");
    Serial.println(advertisedDevice.toString().c_str());

    // We have found a device, let us now see if it contains the service we are looking for.
    if (advertisedDevice.haveServiceUUID() && advertisedDevice.isAdvertisingService(serviceUUID)) {

      //BLEDevice::getScan()->stop();
      myDevice = new BLEAdvertisedDevice(advertisedDevice);
      doConnect = true;
      doScan = false;

    } // Found our server
    BLEDevice::getScan()->stop();
  } // onResult
}; // MyAdvertisedDeviceCallbacks


void setup() {
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");
  BLEDevice::init("");

  // Retrieve a Scanner and set the callback we want to use to be informed when we
  // have detected a new device.  Specify that we want active scanning and start the
  // scan to run for 5 seconds.
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setInterval(1349);
  pBLEScan->setWindow(449);
  pBLEScan->setActiveScan(true);
  pBLEScan->start(5, false);

} // End of setup.

// This is the Arduino main loop function.
void loop() {

  // If the flag "doConnect" is true then we have scanned for and found the desired
  // BLE Server with which we wish to connect.  Now we connect to it.  Once we are 
  // connected we set the connected flag to be true.
  if (doConnect == true) {
    if (connectToServer()) {
      Serial.println("We are now connected to the BLE Server.");
    } else {
      Serial.println("We have failed to connect to the server; there is nothin more we will do.");
    }
    doConnect = false;
  }

  // If we are connected to a peer BLE Server, update the characteristic each time we are reached
  // with the current time since boot.
  if (connected) {
    String newValue = "Time since boot: " + String(millis()/1000);
    Serial.println(newValue);
    
    // Set the characteristic's value to be the array of bytes that is actually a string.
    //pRemoteCharacteristic->writeValue(newValue.c_str(), newValue.length());
  }else if(doScan){
    BLEDevice::getScan()->start(0);  // this is just eample to start scan after disconnect, most likely there is better way to do it in arduino
  }
  
  delay(1000); // Delay a second between loops.
} // End of loop


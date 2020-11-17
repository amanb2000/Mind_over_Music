#include <Arduino.h>
#include <Servo.h>

Servo myservo;
String incomingString;
int oscRate = 50;
int cnt = 0;

void setup() {
  // put your setup code here, to run once:
  myservo.attach(9);

  Serial.begin(9600);
  Serial.setTimeout(100);
}
void loop() {
  cnt++;
  if (Serial.available() > 0) {
      incomingString = Serial.readString();
      oscRate = incomingString.toInt();

      if(oscRate >= 180){
        oscRate = 180;
      }
      else if(oscRate <= 0) {
        oscRate = 0;
      }
  }
  // put your main code here, to run repeatedly:
  int degs = (sin((oscRate/2.5+10)*cnt*0.0004)*90 + 90);

  Serial.println(degs);
  myservo.write(degs);
}
// Port 11 --> YServo
// Port 10 --> Xservo
// Netzteil Braun = +, Blau = GND
// Servo Rot -> +, Braun = GND, Gelb = Data

#include <Servo.h>

String serData;
int incomingIntX = 0;
int incomingIntY = 0;
Servo xServo;  // create servo object to control a servo
Servo yServo;
// output if trigger should be activated
bool trigger;
// twelve servo objects can be created on most boards
const int RELAY_PIN = 7;
int pos = 0;    // variable to store the servo position
String inByte;


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("arduino is ready");
  xServo.attach(10);  // attaches the servo on pin 9 to the servo object
  yServo.attach(11);
  Serial.setTimeout(5);
  //Initialising Relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  Serial.println("ready");
}

void loop() {
  while(Serial.available()>0){
    char rec = Serial.read();
    serData += rec;

    if(rec == '\n'){
      //getting data from string (X direction, Y direction and trigger)
      incomingIntX = gettingX(serData);
      incomingIntY = gettingY(serData);
      trigger = triggertruefalse(serData);
      

      //Servo control
      xServo.write(incomingIntX);
      yServo.write(incomingIntY);
      
      // trigger
      if(trigger == true) {
        digitalWrite(RELAY_PIN, HIGH);
        //delay(5000);
      } else {
        digitalWrite(RELAY_PIN, LOW);
      }
      //Serial.println(incomingIntY);
      //Serial.println("Message received: "+ trigger);
      
      // Returns xServo & yServo Value for Python to calculate new position
      //delay(5);
      //inByte = (String(xServo.read()) + " " + String(yServo.read())); 
      //Serial.println(inByte);*/
      
      serData = "";
    }
  }
}


//functions to clean up variables
//get X
int gettingX(String serData){
  serData.remove(serData.indexOf("Y"));
  serData.remove(serData.indexOf("X"), 1);

  return serData.toInt();
}

//get Y
int gettingY(String serData){
  serData.remove(0, serData.indexOf("Y") + 1);
  
  return serData.toInt();
}

//get trigger
bool triggertruefalse(String serData){
  bool ONOFF = 0;
  if(serData.indexOf("ON") != -1){
    ONOFF = 1;
  } else {
    ONOFF = 0;
  }
  return ONOFF;
}

// Port 11 --> YServo
// Port 10 --> Xservo
// Netzteil Braun = +, Blau = GND
// Servo Rot -> +, Braun = GND, Gelb = Data

#include <Servo.h>

// Compile-time flag: set to 0 to disable relay trigger behavior
#define ENABLE_TRIGGER 1

String serData;
int incomingIntX = 90;
int incomingIntY = 90;
Servo xServo;  // X servo (signal pin 10)
Servo yServo;  // Y servo (signal pin 11)
// output if trigger should be activated
bool trigger = false;
// Relay pin for trigger output
const int RELAY_PIN = 7;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("arduino is ready");
  xServo.attach(10);  // X servo signal pin
  yServo.attach(11);  // Y servo signal pin
  Serial.setTimeout(50); // allow a short timeout for readStringUntil
  // Initialising Relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  Serial.println("ready");
}

void loop() {
  // Read a full line if available (ends with '\n')
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim(); // remove whitespace/newlines

    if (line.length() > 0) {
      // Parse flexible formats like: X90Y95TON  or  X90Y95TOFF  or fallback numeric parts
      int ix = line.indexOf('X');
      int iy = line.indexOf('Y');
      int it = line.indexOf('T');

      int xVal = incomingIntX;
      int yVal = incomingIntY;
      bool trig = false;

      if (ix != -1 && iy != -1 && iy > ix) {
        String sx = line.substring(ix + 1, iy);
        sx.trim();
        xVal = sx.toInt();
      }

      if (iy != -1) {
        int yEnd = (it != -1 && it > iy) ? it : line.length();
        String sy = line.substring(iy + 1, yEnd);
        sy.trim();
        yVal = sy.toInt();
      }

      if (it != -1) {
        String st = line.substring(it + 1);
        st.toUpperCase();
        st.trim();
        if (st.indexOf("ON") != -1 || st.indexOf("1") != -1) {
          trig = true;
        }
      }

      // Clamp values to valid servo range
      xVal = constrain(xVal, 0, 180);
      yVal = constrain(yVal, 0, 180);

      incomingIntX = xVal;
      incomingIntY = yVal;
      trigger = trig;

      // Apply servo positions
      xServo.write(incomingIntX);
      yServo.write(incomingIntY);

#if ENABLE_TRIGGER
      // Control the relay output if feature enabled
      if (trigger) {
        digitalWrite(RELAY_PIN, HIGH);
      } else {
        digitalWrite(RELAY_PIN, LOW);
      }
#endif

      // clear buffer holder (not strictly needed since we used readStringUntil)
      serData = "";
    }
  }
}

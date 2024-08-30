#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(9600); // UART communication setup
  myServo.attach(9); // Attach the servo to pin 9
  myServo.write(0); // Initial position (locked)
}

void loop() {
  if (Serial.available()) {
    char signal = Serial.read(); // Read signal from Arduino 1

    if (signal == '1') {
      myServo.write(90); // Unlock the door
      delay(5000); // Keep the door unlocked for 5 seconds
      myServo.write(0); // Lock the door again
    } else if (signal == '0') {
      myServo.write(0); // Keep the door locked
    }
  }
}
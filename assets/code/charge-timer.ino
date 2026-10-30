int relayPin = 10;

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
}

void loop() {
  digitalWrite(relayPin, LOW);
  delay(240000);
  digitalWrite(relayPin, HIGH);
  delay(60000);
}

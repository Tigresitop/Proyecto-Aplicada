int sensorPin = A0; 
int lecturaRaw = 0;
float humedadPercent = 0.0;

String estado;

int ledNormal = 9;
int ledBajo = 10;

void setup() {
  Serial.begin(9600);  
  pinMode(ledNormal, OUTPUT);
  pinMode(ledBajo, OUTPUT);
}

void loop() {
  lecturaRaw = analogRead(sensorPin); 
  humedadPercent = 100.0 - ((lecturaRaw / 1023.0) * 100.0);

  if (humedadPercent < 0) humedadPercent = 0;
  if (humedadPercent > 100) humedadPercent = 100;
  
  if (humedadPercent < 30) {
    estado = "Bajo";
    digitalWrite(ledBajo, HIGH);     // Encender LED bajo
    digitalWrite(ledNormal, LOW);    // Apagar LED normal
  } else {
    estado = "Normal";
    digitalWrite(ledNormal, HIGH);   // Encender LED normal
    digitalWrite(ledBajo, LOW);      // Apagar LED bajo
  }
  
  Serial.print("Humedad: ");
  Serial.print(humedadPercent, 2);
  Serial.print("%, Estado: ");
  Serial.println(estado);
  
  delay(2000);
}

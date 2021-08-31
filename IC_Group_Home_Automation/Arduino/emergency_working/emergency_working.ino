\
#define NUM_SENSORS 5
String sensors_status[NUM_SENSORS]={"SE1_OFF", "SE2_OFF", "SE3_OFF", "SE4_OFF", "SE5_OFF"};

int motionPin = A3;    // select the input pin for the motion
int touchPin  = A5;    // select the input pin for the touch
int windowPin = A4;    // select the input pin for the window
int gasPin = A1;    // select the input pin for the gas
int firePin   = A2;    // select the input pin for the fire

int ledPin = 13;      // select the pin for the LED

int motionValue = 0;  // variable to store the value coming from the motion sensor
int touchValue  = 0;  // variable to store the value coming from the touch sensor
int windowValue  = 0;  // variable to store the value coming from the touch sensor
int gasValue  = 0;  // variable to store the value coming from the touch sensor
int fireValue  = 0;  // variable to store the value coming from the touch sensor

int touchTimeout = 0;

int sendCommand = 0; // to send command if only there is a change in sensors

void setup() {
    // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  // start serial
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  // read the value from the sensor:
  motionValue = analogRead(motionPin);
  touchValue = analogRead(touchPin);
  windowValue = analogRead(windowPin);
  gasValue = analogRead(gasPin);
  fireValue = analogRead(firePin);


/*********************** Start of Motion Sensor ***********************/
  if(motionValue > 200)
  {
    //Serial.println("SE1_ON");
    sensors_status[0] = "SE1_ON";
    
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    delay(50);
  }
  else
  {
     // turn the ledPin off:
     digitalWrite(ledPin, LOW); 
     //Serial.println("SE1_OFF");
     sensors_status[0] = "SE1_OFF";
  }
 /*********************** End of Motion Sensor ***********************/
 
/*********************** Start of Touch Sensor ***********************/
  if (touchValue > 200)                                                                                                                          
  {
    touchTimeout++;
    if(touchTimeout >= 2)
    {
     // turn the ledPin on
     digitalWrite(ledPin, HIGH);
     Serial.println(touchValue);
     sensors_status[1] = "SE2_ON";
    
     touchTimeout = 0; 
     delay(50);
    }
    else
    {
      // turn the ledPin off:
      digitalWrite(ledPin, LOW);
      //Serial.println("SE2_OFF");
      //sensors_status[1] = "SE2_OFF";
    }
  }
  else
  {
    touchTimeout = 0;
    sensors_status[1] = "SE2_OFF";
  }
/*********************** End of Touch Sensor ***********************/
 
/*********************** Start of Window Sensor ***********************/
  if(windowValue > 200)
  {
    //Serial.println("SE3_ON");
    sensors_status[2] = "SE3_ON";
    
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    delay(50);
  }
  else
  {
     // turn the ledPin off:
     digitalWrite(ledPin, LOW); 
     //Serial.println("SE3_OFF");
     sensors_status[2] = "SE3_OFF";
  }
 /*********************** End of Window Sensor ***********************/

/*********************** Start of Gas Sensor ***********************/
  if(gasValue > 200)
  {
    //sendCommand = 1;
    //Serial.println("SE4_ON");
    sensors_status[3] = "SE4_ON";
    
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    delay(50);
  }
  else
  {
     // turn the ledPin off:
     digitalWrite(ledPin, LOW); 
     //Serial.println("SE4_OFF");
     sensors_status[3] = "SE4_OFF";
  }
 /*********************** End of Gas Sensor ***********************/

/*********************** Start of Fire Sensor ***********************/
  if(fireValue > 200)
  {
    //sendCommand = 1;
    //Serial.println("SE5_ON");
    sensors_status[4] = "SE5_ON";
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    delay(50);
  }
  else
  {
     // turn the ledPin off:
     digitalWrite(ledPin, LOW); 
     //Serial.println("SE5_OFF");
     sensors_status[4] = "SE5_OFF";
  }
 /*********************** End of Gas Sensor ***********************/

  Serial.println(sensors_status[0]);
  Serial.println(sensors_status[1]);
  Serial.println(sensors_status[2]);
  Serial.println(sensors_status[3]);
  Serial.println(sensors_status[4]);
  delay(500);
  
}

#define SWITCH_PIN 3

boolean cmd_end = false;
byte chars[50];
int chars_i = 0;
boolean checking = false;

void setup()
{
  Serial.begin(115200);
  pinMode(SWITCH_PIN, INPUT);
}

void loop()
{
  if (Serial.available() > 0)
  {
    byte inByte = Serial.read();
    if (inByte == 10)
      cmd_end = true;
    else
    {
      chars[chars_i] = inByte;
      chars_i++;
    }
  }
  if (cmd_end)
  {
    cmd_end = false;
    switch (chars[0])
    {
    case 'v': // ACK
      Serial.println("ok");
      checking = true;
      break;
    }
    chars_i = 0;
  }
  if (checking)
  {
    if (digitalRead(SWITCH_PIN))
    {
      Serial.println("y");
    }
    else
      Serial.println("n");
    delay(100);
  }
}

int pow10(int j, byte n[])
{
  int nb = 0;
  for (int k = 0; k < j; k++)
  {
    int ex = 1;
    for (int l = 0; l < j - 1 - k; l++)
      ex *= 10;
    nb += (n[k] - 48) * ex;
  }
  return nb;
}

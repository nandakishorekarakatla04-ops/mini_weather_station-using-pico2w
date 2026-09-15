from machine import Pin, I2C
import sh1106
import time

# I2C0
# GP4 = SDA
# GP5 = SCL
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

# SH1106 OLED 128x64
oled = sh1106.SH1106_I2C(128, 64, i2c)

# Clear display
oled.fill(0)

# Print text
oled.text("OLED TEST", 20, 10)
oled.text("PICO 2WH", 25, 35)

# Show on OLED
oled.show()

while True:
    time.sleep(1)
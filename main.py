from machine import Pin, I2C, ADC
from time import sleep
import dht
import bmp280

# ==========================================
# DHT22
# DATA -> GP2, Physical Pin 4
# ==========================================

dht_sensor = dht.DHT22(Pin(2))


# ==========================================
# BMP280
# SDA -> GP4, Physical Pin 6
# SCL -> GP5, Physical Pin 7
# Address -> 0x76
# ==========================================

i2c_bmp = I2C(
    0,
    scl=Pin(5),
    sda=Pin(4),
    freq=400000
)

bmp = bmp280.BMP280(i2c_bmp, 0x76)


# ==========================================
# LCD 16x2 I2C
# SDA -> GP6, Physical Pin 9
# SCL -> GP7, Physical Pin 10
# ==========================================

i2c_lcd = I2C(
    1,
    scl=Pin(7),
    sda=Pin(6),
    freq=400000
)

LCD_ADDR = 0x27

LCD_BACKLIGHT = 0x08
LCD_ENABLE = 0x04


# ==========================================
# LDR
# GP26 / ADC0 / Physical Pin 31
# ==========================================

ldr = ADC(Pin(26))


# ==========================================
# RAIN SENSOR
# GP27 / ADC1 / Physical Pin 32
# ==========================================

rain = ADC(Pin(27))


# ==========================================
# LCD FUNCTIONS
# ==========================================

def lcd_pulse(data):

    i2c_lcd.writeto(
        LCD_ADDR,
        bytes([data | LCD_ENABLE | LCD_BACKLIGHT])
    )

    i2c_lcd.writeto(
        LCD_ADDR,
        bytes([
            (data & ~LCD_ENABLE) | LCD_BACKLIGHT
        ])
    )


def lcd_send(data, mode):

    high = data & 0xF0
    low = (data << 4) & 0xF0

    lcd_pulse(high | mode)
    lcd_pulse(low | mode)


def lcd_cmd(cmd):

    lcd_send(cmd, 0)


def lcd_data(data):

    lcd_send(data, 1)


def lcd_clear():

    lcd_cmd(0x01)
    sleep(0.002)


def lcd_init():

    sleep(0.05)

    lcd_pulse(0x30)
    sleep(0.01)

    lcd_pulse(0x30)
    sleep(0.01)

    lcd_pulse(0x30)
    sleep(0.01)

    lcd_pulse(0x20)

    lcd_cmd(0x28)
    lcd_cmd(0x0C)
    lcd_cmd(0x06)

    lcd_clear()


def lcd_print(text, row):

    if row == 0:
        lcd_cmd(0x80)
    else:
        lcd_cmd(0xC0)

    text = str(text)
    text = text[:16]

    for char in text:
        lcd_data(ord(char))

    for i in range(16 - len(text)):
        lcd_data(ord(' '))


# ==========================================
# RAIN STATUS
# ==========================================

def get_rain_status(value):

    if value > 50000:
        return "DRY"

    elif value > 35000:
        return "LIGHT"

    elif value > 15000:
        return "MEDIUM"

    else:
        return "HEAVY"


# ==========================================
# LCD START
# ==========================================

lcd_init()

lcd_clear()
lcd_print("MINI WEATHER", 0)
lcd_print("STATION", 1)

sleep(2)


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    try:

        # --------------------------------------
        # DHT22
        # --------------------------------------

        dht_sensor.measure()

        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()


        # --------------------------------------
        # BMP280
        # --------------------------------------

        bmp_temperature = bmp.temperature
        pressure = bmp.pressure / 100


        # --------------------------------------
        # LDR
        # --------------------------------------

        ldr_value = ldr.read_u16()

        light_percent = int(
            ldr_value * 100 / 65535
        )


        # --------------------------------------
        # RAIN SENSOR
        # --------------------------------------

        rain_value = rain.read_u16()

        # IMPORTANT: brackets are required
        rain_status = get_rain_status(rain_value)


        # ======================================
        # SERIAL OUTPUT
        # ======================================

        print()
        print("==============================")
        print("    MINI WEATHER STATION")
        print("==============================")

        print(
            "Temperature:",
            temperature,
            "C"
        )

        print(
            "Humidity:",
            humidity,
            "%"
        )

        print(
            "BMP280 Temp:",
            bmp_temperature,
            "C"
        )

        print(
            "Pressure:",
            pressure,
            "hPa"
        )

        print(
            "LDR ADC:",
            ldr_value
        )

        print(
            "Light:",
            light_percent,
            "%"
        )

        print(
            "Rain ADC:",
            rain_value
        )

        print(
            "Rain Status:",
            rain_status
        )

        print("==============================")


        # ======================================
        # LCD SCREEN 1
        # ======================================

        lcd_clear()

        lcd_print(
            "T:{:.1f}C H:{:.1f}%".format(
                temperature,
                humidity
            ),
            0
        )

        lcd_print(
            "P:{:.0f}hPa".format(
                pressure
            ),
            1
        )

        sleep(3)


        # ======================================
        # LCD SCREEN 2
        # ======================================

        lcd_clear()

        lcd_print(
            "Light:{}%".format(
                light_percent
            ),
            0
        )

        lcd_print(
            "Rain:{}".format(
                rain_status
            ),
            1
        )

        sleep(3)


    except Exception as e:

        print("ERROR:", e)

        lcd_clear()

        lcd_print(
            "SENSOR ERROR",
            0
        )

        lcd_print(
            "CHECK WIRING",
            1
        )

        sleep(2)

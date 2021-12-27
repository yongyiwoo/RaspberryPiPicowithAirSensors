from machine import Pin, SPI, ADC
import utime
import framebuf
import dht11
import co2
import pm
import hcho
import oled

####################################################################################################
# Display resolution
OLED_WIDTH = 96
OLED_HEIGHT = 64
####################################################################################################

####################################################################################################
# Sensor Pins
CO2_PIN = 0
PM_PIN = 1
HCHO_PIN = 2
TH_PIN = 3
####################################################################################################
        
if __name__=='__main__':
    onboard_led = Pin(25, Pin.OUT)
    
    oled_display = oled.SSD1331()
    oled_display.init()
    oled_display.set_windows(0, 0, oled_display.width - 1, oled_display.height - 1)
    
    onboard_led.high()
    utime.sleep(1)
    onboard_led.low()
    
    # oled welcome text
    oled_display.fbuf.fill(0xffff) # bbbb brrr rrrg gggg: 1000 0100 0001 0000
    oled_display.fbuf.text("PLEASE", 24, 24, 0x0000) # bbbb brrr rrrg gggg: 0000 0000 0000 0000
    oled_display.fbuf.text("WAIT", 32, 32, 0x0000)
    oled_display.display_image(oled_display.buffer)
    
    # temperature and humidity
    temp_hum = dht11.DHT11(TH_PIN)
    # carbon dioxide
    co2 = co2.CO2(CO2_PIN)
    # partical matter 2.5
    pm = pm.PM(PM_PIN)
    # formaldehyde
    hcho = hcho.HCHO(HCHO_PIN)
    
    print("Start...")

    while True:
        onboard_led.high()
        utime.sleep(0.1)
        onboard_led.low()
        utime.sleep(0.1)
        onboard_led.high()
        utime.sleep(0.1)
        onboard_led.low()
        
        # Temperature and Humidity
        temp_hum_value = temp_hum.read_data()
        
        temp_value = str(temp_hum_value[0]) + "." + str(temp_hum_value[1])
        hum_value = str(temp_hum_value[2]) + "." + str(temp_hum_value[3])
        
        # Partical matter 2.5
        pm_value = pm.read_data()
        
        # Carbon dioxide
        co2_value = co2.read_data()
        
        # Formaldehyde
        hcho_value = hcho.read_data()
        
        if temp_hum_value == (0, 0, 0, 0):
            continue

        oled_display.fbuf.fill(0x8410) # bbbb brrr rrrg gggg: 1000 0100 0001 0000
        oled_display.fbuf.text("CO2:", 0, 0, 0xffff) # BRRG
        oled_display.fbuf.text(str(int(co2_value)) + "ppm", 40, 0, 0xffff) # BRRG
        
        oled_display.fbuf.text("PM:", 0, 8, 0xffff)
        oled_display.fbuf.text(str(int(pm_value)) + "ug/m3", 40, 8, 0xffff)
        
        oled_display.fbuf.text("HCHO:", 0, 16, 0xffff)
        oled_display.fbuf.text(str(hcho_value) + "ppm", 40, 16, 0xffff)
        
        oled_display.fbuf.text("TEM:", 0, 24, 0xffff)
        oled_display.fbuf.text(temp_value + "c", 40, 24, 0xffff)
        
        oled_display.fbuf.text("HUM:", 0, 32, 0xffff)
        oled_display.fbuf.text(hum_value + "%", 40, 32, 0xffff)
        
        oled_display.fbuf.text("Raspberry", 0, 40, 0x07e0) # bbbb brrr rrrg gggg: 0000 0111 1110 0000
        oled_display.fbuf.text("Pi", 80, 40, 0x001f) # bbbb brrr rrrg gggg: 0000 0000 0001 1111
        oled_display.fbuf.fill_rect(0, 48, 32, 8, 0xffff)
        oled_display.fbuf.text("PICO", 0, 48, 0x0000) # bbbb brrr rrrg gggg: 1111 0111 1101 1110
        oled_display.fbuf.text("with", 40, 48, 0xffff)
        
        oled_display.fbuf.text("Micro", 0, 56, 0xf100)
        oled_display.fbuf.text("Python", 40, 56, 0x07ff)
        
        oled_display.display_image(oled_display.buffer)  
        
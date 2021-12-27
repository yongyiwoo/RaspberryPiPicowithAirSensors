from machine import Pin, SPI
import utime
import time
import framebuf

####################################################################################################
# Display resolution
OLED_WIDTH = 96
OLED_HEIGHT = 64

####################################################################################################
# Pin definition
#SCK_PIN = 10 # SCLK is the SPI communication clock.
#SDI_PIN = 11 # MOSI/SDIN is the data line from the master to the slave in SPI communication.
DC_PIN = 8 # DC is data/command control pin, when DC = 0, write command, when DC = 1, write data.
CS_PIN = 9 # CS is slave chip select, when CS is low, the chip is enabled.

RESET_PIN =  12 # Hardware reset, when it is low, to reset the chip

####################################################################################################
# OLED Display Commands
DRAW_LINE                       = 0x21
DRAW_RECTANGLE                  = 0x22
COPY_WINDOW                     = 0x23
DIM_WINDOW                      = 0x24
CLEAR_WINDOW                    = 0x25
FILL_WINDOW                     = 0x26
DISABLE_FILL                    = 0x00
ENABLE_FILL                     = 0x01
CONTINUOUS_SCROLLING_SETUP      = 0x27
DEACTIVE_SCROLLING              = 0x2E
ACTIVE_SCROLLING                = 0x2F

SET_COLUMN_ADDRESS              = 0x15
SET_ROW_ADDRESS                 = 0x75
SET_CONTRAST_A                  = 0x81
SET_CONTRAST_B                  = 0x82
SET_CONTRAST_C                  = 0x83
MASTER_CURRENT_CONTROL          = 0x87
SET_PRECHARGE_SPEED_A           = 0x8A
SET_PRECHARGE_SPEED_B           = 0x8B
SET_PRECHARGE_SPEED_C           = 0x8C
SET_REMAP                       = 0xA0
SET_DISPLAY_START_LINE          = 0xA1
SET_DISPLAY_OFFSET              = 0xA2
NORMAL_DISPLAY                  = 0xA4
ENTIRE_DISPLAY_ON               = 0xA5
ENTIRE_DISPLAY_OFF              = 0xA6
INVERSE_DISPLAY                 = 0xA7
SET_MULTIPLEX_RATIO             = 0xA8
DIM_MODE_SETTING                = 0xAB
SET_MASTER_CONFIGURE            = 0xAD
DIM_MODE_DISPLAY_ON             = 0xAC
DISPLAY_OFF                     = 0xAE
NORMAL_BRIGHTNESS_DISPLAY_ON    = 0xAF
POWER_SAVE_MODE                 = 0xB0
PHASE_PERIOD_ADJUSTMENT         = 0xB1
DISPLAY_CLOCK_DIV               = 0xB3
SET_GRAy_SCALE_TABLE            = 0xB8
ENABLE_LINEAR_GRAY_SCALE_TABLE  = 0xB9
SET_PRECHARGE_VOLTAGE           = 0xBB

SET_V_VOLTAGE                   = 0xBE

####################################################################################################

class SSD1331(object):
    def __init__(self):
        self.width = OLED_WIDTH
        self.height = OLED_HEIGHT
        
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        self.reset_pin = Pin(RESET_PIN, Pin.OUT)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        
        # Initialize SPI
        self.spi = SPI(1)
        
        # Buffer size
        self.buffer = bytearray(self.width * self.height * 2)
        # Initialize framebuf
        self.fbuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        
    # Write value to the pin
    def digital_write(self, pin, value):
        pin.value(value)

    # Read value from the pin
    def digital_read(self, pin):
        return pin.value()

    # SPI write bytes
    def spi_write(self, data):
        self.spi.write(bytearray(data))
        
    # Write command dc_pin low, cs_pin low
    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.spi_write([command])
    
    # Write data dc_pin high, cs_pin low
    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.spi_write([data])   
    
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        utime.sleep_ms(100)
        self.digital_write(self.reset_pin, 0)
        utime.sleep_ms(100)
        self.digital_write(self.reset_pin, 1)
        
    def init(self):
        # Chip select set to 0 to enable the display
        self.digital_write(self.cs_pin, 0)
        # Reset the display
        self.reset()
        
        # Command sequence
        self.send_command(DISPLAY_OFF)          #Display Off
        self.send_command(SET_CONTRAST_A)       #Set contrast for color A
        self.send_command(0xFF)                     #145 0x91
        self.send_command(SET_CONTRAST_B)       #Set contrast for color B
        self.send_command(0xFF)                     #80 0x50
        self.send_command(SET_CONTRAST_C)       #Set contrast for color C
        self.send_command(0xFF)                     #125 0x7D
        self.send_command(MASTER_CURRENT_CONTROL) #master current control
        self.send_command(0x06)                     #6
        self.send_command(SET_PRECHARGE_SPEED_A) #Set Second Pre-change Speed For ColorA
        self.send_command(0x64)                     #100
        self.send_command(SET_PRECHARGE_SPEED_B) #Set Second Pre-change Speed For ColorB
        self.send_command(0x78)                     #120
        self.send_command(SET_PRECHARGE_SPEED_C) #Set Second Pre-change Speed For ColorC
        self.send_command(0x64)                     #100
        self.send_command(SET_REMAP)            #set remap & data format
        self.send_command(0x72)                     #0x72              
        self.send_command(SET_DISPLAY_START_LINE) #Set display Start Line
        self.send_command(0x0)
        self.send_command(SET_DISPLAY_OFFSET)   #Set display offset
        self.send_command(0x0)
        self.send_command(NORMAL_DISPLAY)       #Set display mode
        self.send_command(SET_MULTIPLEX_RATIO)  #Set multiplex ratio
        self.send_command(0x3F)
        self.send_command(SET_MASTER_CONFIGURE) #Set master configuration
        self.send_command(0x8E)
        self.send_command(POWER_SAVE_MODE)      #Set Power Save Mode
        self.send_command(0x00)                     #0x00
        self.send_command(PHASE_PERIOD_ADJUSTMENT) #phase 1 and 2 period adjustment
        self.send_command(0x31)                     #0x31
        self.send_command(DISPLAY_CLOCK_DIV)    #display clock divider/oscillator frequency
        self.send_command(0xF0)
        self.send_command(SET_PRECHARGE_VOLTAGE) #Set Pre-Change Level
        self.send_command(0x3A)
        self.send_command(SET_V_VOLTAGE)        #Set vcomH
        self.send_command(0x3E)
        self.send_command(DEACTIVE_SCROLLING)   #disable scrolling
        self.send_command(NORMAL_BRIGHTNESS_DISPLAY_ON) #set display onH
        
    # Set windows address
    def set_windows(self, x_start, y_start, x_end, y_end):
        self.send_command(SET_COLUMN_ADDRESS)
        self.send_command(x_start)         #cloumn start address
        self.send_command(x_end)  #cloumn end address
        self.send_command(SET_ROW_ADDRESS)
        self.send_command(y_start)         #page atart address
        self.send_command(y_end) #page end address
                
    def display_image(self, image):      
        for i in range(0, len(self.buffer)):
            self.send_data(image[i])

if __name__=='__main__':
    oled = SSD1331()
    oled.init()
    oled.set_windows(0, 0, oled.width - 1, oled.height - 1)
    
    # oled welcome text
    oled.fbuf.fill(0xffff) # bbbb brrr rrrg gggg: 1000 0100 0001 0000
    oled.fbuf.text("PLEASE", 24, 24, 0x0000) # bbbb brrr rrrg gggg: 0000 0000 0000 0000
    oled.fbuf.text("WAIT", 32, 32, 0x0000)
    oled.display_image(oled.buffer)
    
  
        
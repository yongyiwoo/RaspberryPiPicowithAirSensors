from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import utime


class HCHO(object):
    # PIO assembler
    # HCHO datasheet, HCHO PWM section
    @staticmethod
    @asm_pio(autopush=True, push_thresh=1) # auto push to RX FIFO when 8 bits
    def hcho_bit_reader():
        # PM sensor start signal (0.2 ms per cycle)
        wait(0,pin,0) [4]# Wait for bit 0 (bit index [0]) from pin become 0, the end of cycle
        wait(1,pin,0) [9]# Wait for bit 0 (bit index [0]) from pin become 1, the start of cycle
        label("read_bit")
        jmp(pin, "1")
        # If the pin is low        
        in_(0,1) # Shift Pin 1 bit to ISR
        jmp("read_bit") [2]
        # If the pin is high
        label("1")
        in_(0,1) # Shift Pin 1 bit to ISR
        #
        jmp("read_bit") [2]
        

    def __init__(self, hcho_pin_number):
        self.hcho_pin_number = hcho_pin_number       
        
    def read_data(self):
        # Set to read
        self.hcho_pin = Pin(self.hcho_pin_number, Pin.IN, Pin.PULL_UP)
        # There are 2 PIOs, each PIO has 4 state machines, the StateMachine id is from 0-3(1st PIO), 4-7(2nd PIO)
        # Each PIO can have up to 32 instructions
        hcho_meta_data = StateMachine(3, self.hcho_bit_reader, freq = 5000, in_base=self.hcho_pin, jmp_pin=self.hcho_pin)

        hcho_meta_data.active(1) # State Machine starts
        hcho_data = 0
        hcho_list = []
        for _ in range(1500):
            hcho_list.append(hcho_meta_data.get())
            hcho_data += hcho_meta_data.get()
            #print(pm_data)

        hcho_meta_data.active(0) # State Machine ends
        
        hcho_value = round(0.0008 * hcho_data, 2)
        
        return hcho_value
        
if __name__=='__main__':
    formaldehyde = HCHO(2)
    while True:
        print(formaldehyde.read_data())
        #utime.sleep(5)


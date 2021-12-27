from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import utime


class CO2(object):
    # PIO assembler
    # CO2 datasheet, CO2 PWM section
    @staticmethod
    @asm_pio(autopush=True, push_thresh=1) # auto push to RX FIFO when 1 bits
    def co2_bit_reader():
        # CO2 sensor start signal (0.2 ms per cycle)
        wait(0,pin,0) [9] # Wait for bit 0 (bit index [0]) from pin become 0, the end of cycle
        wait(1,pin,0) [9] # Wait for bit 0 (bit index [0]) from pin become 1, the start of cycle
        label("read_bit")
        jmp(pin, "1")
        # If the pin is low
        in_(0,1) # Shift Pin 1 bit to ISR
        jmp("read_bit") [2]
        # If the pin is high
        label("1")
        in_(0,1) # Shift Pin 1 bit to ISR
        jmp("read_bit") [2]
        

    def __init__(self, co2_pin_number):
        self.co2_pin_number = co2_pin_number       
        
    def read_data(self):
        # Set to read
        self.co2_pin = Pin(self.co2_pin_number, Pin.IN, Pin.PULL_UP)
        # There are 2 PIOs, each PIO has 4 state machines, the StateMachine id is from 0-3(1st PIO), 4-7(2nd PIO)
        # Each PIO can have up to 32 instructions
        co2_meta_data = StateMachine(1, self.co2_bit_reader, freq = 5000, in_base=self.co2_pin, jmp_pin=self.co2_pin)

        co2_meta_data.active(1) # State Machine starts
        co2_data = 0 # Set a "1" counter
        
        for _ in range(1000):
            co2_data += co2_meta_data.get()

        co2_meta_data.active(0) # State Machine ends

        co2_value = 5000 * co2_data // 1000
        
        return co2_value
        
if __name__=='__main__':
    cd = CO2(0)
    while True:
        print(cd.read_data())
        #utime.sleep(5)

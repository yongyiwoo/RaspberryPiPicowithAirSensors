from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import utime

class DHT11(object):
    # PIO assembler
    # DHT11 datasheet, DHT11 sensor response section
    @staticmethod
    @asm_pio(autopush=True, push_thresh=8) # auto push to RX FIFO when 8 bits
    def dht11_bit_reader():
        #print("pioasm")
        # DHT11 sensor response signal
        wait(0,pin,0) # Wait for bit 0 (bit index [0]) from pin become 0, last 80 us
        wait(1,pin,0) # Wait for bit 0 (bit index [0]) from pin become 1, last 80 us    
        # DHT11 send data from a 0 for 50 us
        # If pin changes from high to low within 28us is 0, otherwise 1
        label("read_bit")
        wait(1,pin,0) [27] # Wait instruction needs 1 cycle (1 us), and then wait for 27 cycles (27 us)
        jmp(pin, "high_detected")
        
        # Recognize as 0, back to read next bit
        label("low_detected")
        in_(0,1) # Shift Pin 1 bit to ISR
        wait(0,pin,0)
        jmp("read_bit")

        # Recognize as 1, back to read next bit
        label("high_detected")
        in_(0,1) # Shift Pin 1 bit to ISR
        wait(0,pin,0)
        jmp("read_bit")
    
    def __init__(self, ht_pin_number):
        #print("__init__")
        self.ht_pin_number = ht_pin_number       
        
    def read_data(self):
        # MCU sends 28 ms low signal
        self.ht_pin = Pin(self.ht_pin_number, Pin.OUT, Pin.PULL_DOWN)
        self.ht_pin.value(0)
        utime.sleep_ms(18)
        # Set to read with high signal (20-40 us)
        self.ht_pin = Pin(self.ht_pin_number, Pin.IN, Pin.PULL_UP)

        # There are 2 PIOs, each PIO has 4 state machines, the StateMachine id is from 0-3(1st PIO), 4-7(2nd PIO)
        # Each PIO can have up to 32 instructions
        ht_meta_data = StateMachine(0, self.dht11_bit_reader, freq = 1000000, in_base=self.ht_pin, jmp_pin=self.ht_pin)

        ht_meta_data.active(1) # State Machine starts
        ht_data = []
        for _ in range(5):
            ht_data.append(bin(ht_meta_data.get()))
            #print(ht_data)

        ht_meta_data.active(0) # State Machine ends
        #print(ht_data)
        
        if int(ht_data[0]) + int(ht_data[1]) + int(ht_data[2]) + int(ht_data[3]) == int(ht_data[4]):
            return (int(ht_data[2]), int(ht_data[3]), int(ht_data[0]), int(ht_data[1]))
        else:
            return (0,0,0,0)
        
if __name__=='__main__':
    temp_hum = DHT11(3)
    while True:
        print(temp_hum.read_data())
        #utime.sleep(2)
    


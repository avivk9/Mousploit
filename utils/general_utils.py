"""
This file contains miscellaneous utility functions and definitions.
"""

# constants
PING_PAYLOAD = [0x0F, 0x0F, 0x0F, 0x0F] # the arbitrary ping payload used in find_frequency_channel() and sniff()
CHANNELS = range(2, 84) # the range of channels used in channel sweeping, scanning and sniffing (why this range was chosen is explained in find_frequency_channel())

def format_bytes(data):
    # e.g. the payload: [0x00, 0xC1, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3B] is formatted as: 00:C1:00:04:00:00:00:00:00:3B
    return ':'.join('{:02X}'.format(b) for b in data)

def payload_str_to_bytes(payload):
    # e.g. the payload string: 00:C1:00:04:00:00:00:00:00:3B is converted to: [0x00, 0xC1, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3B]
    return list(bytes.fromhex(payload.replace(':', '')))

def address_str_to_bytes(rf_address):
    # e.g. the RF address E4:ED:AE:B8:B4 is converted to: [0xB4, 0xB8, 0xAE, 0xED, 0xE4]
    return payload_str_to_bytes(rf_address)[::-1]

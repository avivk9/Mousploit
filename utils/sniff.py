import time
from .general_utils import *

DWELL_TIME = 0.1 # How long (in seconds) the radio listens for packets per channel

def from_display(data):
    return [int(b, 16) for b in data.split(':')]

def to_display(data):
        return ':'.join('{:02X}'.format(x) for x in data)

def sniff(radio, address, duration=20):
    """
    This function receives radio parameter, the duration of the sniffing proccess (in seconds),
    and the address of the vulnerable device. It performs packet sniffing from the vulnerable device with the address given.
    """

    radio.enter_sniffer_mode(address_str_to_bytes(address))

    channels = range(2, 84)

    channel_index = 0
    radio.set_channel(channels[channel_index])
    last_channel_switch = time.time() # Variable to store the last time the radio switched to another channel
    start_time = time.time() # Variable to store the time in which the scan has started

    while time.time() - start_time < duration: # Repeat until the time given in the duration variable has passed
        if len(channels) > 1 and time.time() - last_channel_switch > DWELL_TIME:
            if not radio.transmit_payload(PING_PAYLOAD):
                for channel_index in range(len(channels)):
                    radio.set_channel(channels[channel_index]) # Change channel
                    if radio.transmit_payload(PING_PAYLOAD):
                        last_channel_switch = time.time()
                        break
            else:
                last_channel_switch = time.time() # Updating the variable

        try:
            value = radio.receive_payload() # Try to receive payload
        except RuntimeError:
            value = [1]

        if value[0] == 0:
            # Stay on channel
            last_channel_switch = time.time() + 5.0
            payload = value[1:]
            print(f"address: {address}    packet: {to_display(payload)}")
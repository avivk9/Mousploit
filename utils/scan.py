import time
from .general_utils import *

DWELL_TIME = 0.1 # how long (in seconds) the radio listens for packets per channel

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

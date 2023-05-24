import time
from .general_utils import *
from .injection_utils import find_frequency_channel # sniffing is the only case where find_frequency_channel is used not in the context of injection attacks
from .packet_identifier import *
from .vendors import eagletec

TIMEOUT = 0.1 # how long (in seconds) the radio can stay on the current channel before it needs to send a ping or find the channel again, because it's been too long since a packet was received

def sniff(radio, address, duration=20):
    """
    This function receives a radio parameter (can either be a RadioServer for remote communication, or nrf24 for local usage),
    the duration of the sniffing proccess (in seconds), and the address of a vulnerable device.
    It performs packet sniffing - printing packets that arrive from that particular device within the given time duration.
    Sniffing is much more sensitive than scanning, so we should be able to observe packets resulting from even the slightest mouse movement.
    """

    # MOSART-based devices (like EagleTec) have 4-byte addresses
    if len(address) == 4:
        eagletec.sniff(radio, address, duration)
        return

    radio.enter_sniffer_mode(address) # sending a command to enter sniffer mode with the given address

    # starting from the first channel
    channel_index = 0
    radio.set_channel(CHANNELS[channel_index])

    channel_timer = time.time() # variable that stores the last time a ping succeeded or a packet was successfully received (time.time() returns the current time)
    start_time = time.time() # variable to store the time in which the sniffing process has started

    while time.time() - start_time < duration: # repeating as long as the time passed since the beginning of the sniffing process has not exceeded the desired duration

        if time.time() - channel_timer > TIMEOUT: # if the timer hasn't been reset in a long time (by receiving a packet)

            # Try transmitting a ping payload. If it's unsuccessful, try to find the channel again.
            # When testing some Microsoft keyboards/mice, we observed that sometimes there are channels for which the initial ping or find_channel is successful
            # even though the channel is not actually used by the keyboard at that moment. As a result, the channel timer is reset, but payloads cannot be
            # received successfully. When the timeout is reached, the initial ping succeeds again and we keep using the same dysfunctional channel.
            # This situation may continue until the sniffing ends, preventing packets from being received.
            # It turned out that setting the optional parameters of transmit_payload (such as number of retransmits) to a minimum, drastically reduces the chances
            # of the initial ping to succeed, and allows the radio to go searching for the right channel. It is also useful for the pings sent by find_channel itself.
            if not radio.transmit_payload(PING_PAYLOAD, 1, 1):
                if find_frequency_channel(radio, 1, 1):
                    channel_timer = time.time() # a channel was found, reset the timer
            else:
                channel_timer = time.time() # initial ping was successful, reset the timer

        value = radio.receive_payload() # try to receive a payload

        # If you take a look at the research firmware code here: https://github.com/BastilleResearch/nrf-research-firmware/blob/master/src/radio.c#L265
        # You can deduce that the first byte returned by receive_payload indicates whether or not the payload is valid. 0 means it's valid.
        if value[0] == 0:
            # Reset the timer, but add a little bit of time so that the radio doesn't start pinging or looking for channels 0.1 seconds after we leave the mouse/keyboard...
            # But it also shouldn't be too long, to allow searching for the channel ASAP in case it was actually lost.
            channel_timer = time.time() + 3.0

            payload = value[1:] # split the payload from the status byte
            if len(payload) > 0: # some packets containing no payload have been observed, so we don't want to print them
                print(f"address: {format_bytes(address[::-1])}    packet: {format_bytes(payload):<65}    type: {types[identify_type(payload)]}") # address is a list of bytes in little endian, so reverse it

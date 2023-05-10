import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from radio_agent import nrf24
from utils.general_utils import *
from utils.vendors.eagletec import *

MOVEMENT_FRAME_TYPE = 0x04
MOVEMENT_PACKET_LEN = 14
KEYPRESS_PACKET_LEN = 12
THRESHOLD = 5

def main():
    # initialize the radio
    radio = nrf24.nrf24()

    radio.enter_promiscuous_mode_generic([0xAA, 0xAA], RF_RATE_1M)
    radio.set_channel(CHANNEL)

    addresses = {}

    while True:
        value = radio.receive_payload()
        if value[0] == 0xFF:
            continue

        is_dongle_packet = False
        for i in range(len(value)):
            if list(value[i:i+2]) == [0x4B, 0x78]:
                is_dongle_packet = True
                break
        if is_dongle_packet:
            continue

        if POSTAMBLE in value and value.index(POSTAMBLE) + 1 in [MOVEMENT_PACKET_LEN, KEYPRESS_PACKET_LEN]:
            value = value[:value.index(POSTAMBLE)+1]

            frame_type = (value[6] ^ WHITENING_BYTE) >> 4
            key_state = value[7] ^ WHITENING_BYTE
            if key_state in [KEY_STATE_DOWN, KEY_STATE_UP] or frame_type == MOVEMENT_FRAME_TYPE:
                address = format_bytes(value[2:6])
                print(f"address: {address}    packet: {format_bytes(value):<20}")
                if not address in addresses:
                    addresses[address] = 0
                addresses[address] += 1
                if addresses[address] >= THRESHOLD:
                    print(f"Found device address: {address}")
                    break

if __name__ == "__main__":
    main()

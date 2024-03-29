#--------------DON'T IMPORT THIS FILE ANYWHERE--------------

import usb

# USB commands
ENTER_TONE_TEST_MODE           = 0x07
TRANSMIT_ACK_PAYLOAD           = 0x08
TRANSMIT_PAYLOAD_GENERIC       = 0x0C
ENTER_PROMISCUOUS_MODE_GENERIC = 0x0D

# nRF24LU1+ registers
RF_CH = 0x05

# nRF24LU1+ radio dongle
class nrf24:

    # Sufficiently long timeout for use in a VM
    usb_timeout = 2500

    # Put the radio into continuous tone (TX) test mode
    def enter_tone_test_mode(self):
        self.send_usb_command(ENTER_TONE_TEST_MODE, [])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        print('Entered continuous tone test mode')

    # Transmit a generic (non-ESB) payload
    def transmit_payload_generic(self, payload, address="\x33\x33\x33\x33\x33"):
        data = [len(payload), len(address)] + map(ord, payload) + map(ord, address)
        self.send_usb_command(TRANSMIT_PAYLOAD_GENERIC, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0
    
    # Transmit an ESB ACK payload
    def transmit_ack_payload(self, payload):
        data = [len(payload)] + map(ord, payload)
        self.send_usb_command(TRANSMIT_ACK_PAYLOAD, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0
   
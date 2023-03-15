'''
  Copyright (C) 2016 Bastille Networks

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
This is a modified version of the original nrf24.py from MouseJack:
1. Removed PyUSB dependency check.
2. Removed import of logging module, replaced logging.debug() calls with print().
3. Original code is in Python 2, made small changes to support Python 3.
4. Moved unused constants and functions to unused.py.
'''

import usb

# USB commands
TRANSMIT_PAYLOAD       = 0x04
ENTER_SNIFFER_MODE     = 0x05
ENTER_PROMISCUOUS_MODE = 0x06
SET_CHANNEL            = 0x09
GET_CHANNEL            = 0x0A
ENABLE_LNA_PA          = 0x0B
RECEIVE_PAYLOAD        = 0x12

# nRF24LU1+ radio dongle
class nrf24:
    
    # Sufficiently long timeout for use in a VM
    usb_timeout = 2500
    
    # Constructor
    def __init__(self, index=0):
        try:
            self.dongle = list(usb.core.find(idVendor=0x1915, idProduct=0x0102, find_all=True))[index]
            self.dongle.set_configuration()
        except usb.core.USBError as ex:
            raise ex
        except:
            raise Exception('Cannot find USB dongle.')
    
    # Put the radio in pseudo-promiscuous mode
    def enter_promiscuous_mode(self, prefix=[]):
        self.send_usb_command(ENTER_PROMISCUOUS_MODE, [len(prefix)] + map(ord, prefix))
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        if len(prefix) > 0:
            print('Entered promiscuous mode with address prefix {0}'.format(':'.join('{:02X}'.format(ord(b)) for b in prefix)))
        else:
            print('Entered promiscuous mode')
    
    # Put the radio in ESB "sniffer" mode (ESB mode w/o auto-acking)
    def enter_sniffer_mode(self, address):
        self.send_usb_command(ENTER_SNIFFER_MODE, [len(address)] + map(ord, address))
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        print('Entered sniffer mode with address {0}'.format(':'.join('{:02X}'.format(ord(b)) for b in address[::-1])))
    
    # Receive a payload if one is available
    def receive_payload(self):
        self.send_usb_command(RECEIVE_PAYLOAD, ())
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
    
    # Transmit an ESB payload
    def transmit_payload(self, payload, timeout=4, retransmits=15):
        data = [len(payload), timeout, retransmits] + map(ord, payload)
        self.send_usb_command(TRANSMIT_PAYLOAD, data)
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)[0] > 0
     
    # Set the RF channel
    def set_channel(self, channel):
        if channel > 125:
            channel = 125
        self.send_usb_command(SET_CHANNEL, [channel])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
        print('Tuned to {0}'.format(channel))
    
    # Get the current RF channel
    def get_channel(self):
        self.send_usb_command(GET_CHANNEL, [])
        return self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
    
    # Enable the LNA (CrazyRadio PA)
    def enable_lna(self):
        self.send_usb_command(ENABLE_LNA_PA, [])
        self.dongle.read(0x81, 64, timeout=nrf24.usb_timeout)
    
    # Send a USB command
    def send_usb_command(self, request, data):
        data = [request] + list(data)
        self.dongle.write(0x01, data, timeout=nrf24.usb_timeout)
    
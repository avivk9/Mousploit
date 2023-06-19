"""
After the first time we ran the radio agent on the Raspberry Pi Zero W, we got the following error when trying to run it again
(occurring when the radio gets initialized):

usb.core.USBTimeoutError: [Errno 110] Operation timed out

To solve it, the USB device needs to be reset each time we run the agent. This can be done by using the ioctl system call of Linux,
with a request code that resets the given USB device.
Everything here only applies to Linux systems (as the one used by Pi Zero W). No reset is performed when the agent runs on a Windows system
(this file is not even imported when running on Windows, as it would cause an error).

References:
https://stackoverflow.com/questions/14626395/how-to-properly-convert-a-c-ioctl-call-to-a-python-fcntl-ioctl-call
https://gist.github.com/PaulFurtado/fce98aef890469f34d51
"""

import fcntl
import usb

# equivalent of the _IO('U', 20) constant in the Linux kernel
USBDEVFS_RESET = ord('U') << (4 * 2) | 20

def reset_nrf24(index=0):
    dongle = list(usb.core.find(idVendor=0x1915, idProduct=0x0102, find_all=True))[index] # find the Research Firmware dongle
    busnum = dongle.bus
    devnum = dongle.address
    filename = f"/dev/bus/usb/{busnum:03d}/{devnum:03d}" # for communicating with the device through a file descriptor
    fd = open(filename, "wb")
    fcntl.ioctl(fd, USBDEVFS_RESET, 0) # reset
    fd.close()

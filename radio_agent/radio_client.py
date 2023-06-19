import socket
import platform # module for retrieving data about the current platform
import nrf24

# custom codes for possible commands that the server can send to the agent
ENTER_PROMISCUOUS_MODE         = 1
ENTER_PROMISCUOUS_MODE_GENERIC = 2
ENTER_SNIFFER_MODE             = 3
RECEIVE_PAYLOAD                = 4
TRANSMIT_PAYLOAD               = 5
SET_CHANNEL                    = 6
GET_CHANNEL                    = 7

# constants
IP = "127.0.0.1" # change to PC address (in the LAN created by the hotspot) when using Pi Zero W as agent
PORT = 5000
BUF_SIZE = 1024 # for recv parameter
ACK = 1 # for informing the server that the command was carried out successfully, in case there's no specific data it needs to return
DEBUG = False # enable/disable debug prints

def debug_print(msg):
    if DEBUG:
        print(msg)

# this function receives a disconnected socket, closes it and repeatedly tries to reconnect to the server
def reconnect(sock):
    while True:
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cannot reuse a closed socket, so initialize a new one
        sock.settimeout(0.5) # setting a timeout of 0.5sec before the socket gives up the current connection attempt
        try:
            sock.connect((IP, PORT)) # blocks until either the timeout expires (and a timeout exception is raised) or the connection is successful
            print("\nConnected!")
            return sock
        except socket.timeout:
            print(".", end="", flush=True) # print dots as long as the client is trying to connect

def main():
    # in case the client runs in the Pi Zero W, we need to reset the radio
    if platform.system() == "Linux":
        import usb_reset
        usb_reset.reset_nrf24()

    # initialize the radio
    radio = nrf24.nrf24()

    # initialize TCP socket (not connecting it already, which allows us to run the client before the server and wait until connection as part of reconnect())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        # listening to commands from the server
        try:
            data = sock.recv(BUF_SIZE) # blocking call, as sockets are blocking by default (could be changed)
        except socket.error:
            sock = reconnect(sock) # try to reconnect
            continue # after reconnection is successful, start waiting for messages again

        if len(data) == 0: # means the server has closed (or is in the process of closing) the connection
            print("Connection closed by the server.")
            sock.close() # closing socket so that in the next iteration there will be an exception, causing reconnection
            continue
        
        if data[0] == ENTER_PROMISCUOUS_MODE:
            debug_print("Received: ENTER_PROMISCUOUS_MODE")
            radio.enter_promiscuous_mode()
            sock.sendall(bytes([ACK]))

        elif data[0] == ENTER_PROMISCUOUS_MODE_GENERIC:
            debug_print("Received: ENTER_PROMISCUOUS_MODE_GENERIC")
            prefix_len = data[1]
            rate = data[2]
            payload_length = data[3]
            prefix = list(data[4:4 + prefix_len])
            radio.enter_promiscuous_mode_generic(prefix, rate, payload_length)
            sock.sendall(bytes([ACK]))

        elif data[0] == ENTER_SNIFFER_MODE:
            debug_print("Received: ENTER_SNIFFER_MODE")
            address_len = data[1]
            address = list(data[2:2 + address_len]) # we have to convert bytes to list before passing the address as parameter to enter_sniffer_mode()
            debug_print(f"Address: {address}")
            radio.enter_sniffer_mode(address)
            sock.sendall(bytes([ACK]))

        elif data[0] == RECEIVE_PAYLOAD:
            debug_print("Received: RECEIVE_PAYLOAD")
            payload = radio.receive_payload() # return type is array.array (because it's the return type of PyUSB read())
            sock.sendall(payload.tobytes()) # array.array can be converted to bytes using its tobytes() method

        elif data[0] == TRANSMIT_PAYLOAD:
            debug_print("Received: TRANSMIT_PAYLOAD")
            payload_len = data[1]
            timeout = data[2]
            retransmits = data[3]
            payload = list(data[4:4 + payload_len]) # we have to convert bytes to list before passing the payload as parameter to transmit_payload()
            debug_print(f"Payload: {payload}")
            ret = radio.transmit_payload(payload, timeout, retransmits) # return value determines whether an ACK response was received from the dongle. We should forward it as-is to the server
            sock.sendall(bytes([ret]))

        elif data[0] == SET_CHANNEL:
            channel = data[1]
            debug_print(f"Received: SET_CHANNEL. Channel: {channel}")
            radio.set_channel(channel)
            sock.sendall(bytes([ACK]))

        elif data[0] == GET_CHANNEL:
            debug_print(f"Received: GET_CHANNEL")
            channel = radio.get_channel()
            sock.sendall(bytes([channel]))

if __name__ == "__main__":
    main()

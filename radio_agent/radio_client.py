import socket
import time
import nrf24

# custom codes for possible commands that the server can send to the agent
ENTER_PROMISCUOUS_MODE = 1
ENTER_SNIFFER_MODE     = 2
RECEIVE_PAYLOAD        = 3
TRANSMIT_PAYLOAD       = 4
SET_CHANNEL            = 5
GET_CHANNEL            = 6

# constants
IP = "127.0.0.1"
PORT = 5000
BUF_SIZE = 1024 # for recv parameter
ACK = 1 # for informing the server that the command was carried out successfully, in case there's no specific data it needs to return
DEBUG = False # enable/disable debug prints

def debug_print(msg):
    if DEBUG:
        print(msg)

# this function receives a defunct socket, closes it and repeatedly tries to reconnect to the server
def reconnect(sock):
    sock.close()
    print("Connecting... (Press Ctrl+Break to exit)")
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cannot reuse a closed socket, so initialize a new one
            sock.connect((IP, PORT)) # blocks until some timeout expires and an exception is raised
            return sock # if we reached here, connection was successful
        except:
            time.sleep(1) # sleeping for 1sec before next try

def main():
    # initialize the radio
    radio = nrf24.nrf24()

    # initialize TCP socket (not connecting it already, in order to take advantage of the infinite loop in reconnect())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        # listening to commands from the server
        try:
            data = sock.recv(BUF_SIZE) # blocking call, as sockets are blocking by default (could be changed)
        except:
            sock = reconnect(sock) # try to reconnect
            continue # after reconnection is successful, start waiting for messages again

        if len(data) == 0: # means the server has closed (or is in the process of closing) the connection
            print("Connection closed by the server.")
            sock = reconnect(sock)
            continue
        
        if data[0] == ENTER_PROMISCUOUS_MODE:
            debug_print("Received: ENTER_PROMISCUOUS_MODE")
            radio.enter_promiscuous_mode()
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
            payload = list(data[2:2 + payload_len]) # we have to convert bytes to list before passing the payload as parameter to transmit_payload()
            debug_print(f"Payload: {payload}")
            ret = radio.transmit_payload(payload) # return value determines whether an ACK response was received from the dongle. We should forward it as-is to the server
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

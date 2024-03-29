import socket

# custom codes for possible commands that the server can send to the agent
ENTER_PROMISCUOUS_MODE         = 1
ENTER_PROMISCUOUS_MODE_GENERIC = 2
ENTER_SNIFFER_MODE             = 3
RECEIVE_PAYLOAD                = 4
TRANSMIT_PAYLOAD               = 5
SET_CHANNEL                    = 6
GET_CHANNEL                    = 7

# constants
BUF_SIZE = 1024 # for recv parameter
ERROR = 0

class RadioServer:
    def __init__(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket
        sock.bind((ip, port))
        sock.listen(1) # at most one pending connection request
        print(f"Listening on {ip}, port {port}...")
        conn, addr = sock.accept()
        self.connection = conn # storing connection as a data member for sending/receiving messages
        print(f"Received connection from {addr}")
    
    # In order to implement a synchronized protocol, the server will always wait for a response after sending a command to the client,
    # by calling the following function in all command functions below. For commands that don't expect some specific return data,
    # the client will respond with a simple ACK.
    def get_response(self):
        try:
            data = self.connection.recv(BUF_SIZE) # since recv is a blocking call, all command functions will not return before receiving a response
            if len(data) == 1: # could be ACK or return value of transmit_payload/get_channel
                return data[0]
            return list(data) # must be a payload returned from receive_payload(), so converting bytes to list
        except:
            print("Error detected. Closing connection.")
            self.connection.close()
            return (ERROR)

    def enter_promiscuous_mode(self):
        self.connection.sendall(bytes([ENTER_PROMISCUOUS_MODE]))
        return self.get_response()
    
    def enter_promiscuous_mode_generic(self, prefix, rate, payload_length=32):
        self.connection.sendall(bytes([ENTER_PROMISCUOUS_MODE_GENERIC, len(prefix), rate, payload_length] + prefix))
        return self.get_response()

    def enter_sniffer_mode(self, rf_address):
        # Sending the length of the data before the data itself because it's common to do so.
        # This way the client knows how many bytes to read and doesn't make any assumptions.
        self.connection.sendall(bytes([ENTER_SNIFFER_MODE, len(rf_address)] + rf_address)) # rf_address is a list, so it's concatenated
        return self.get_response()

    def receive_payload(self):
        self.connection.sendall(bytes([RECEIVE_PAYLOAD]))
        payload = self.get_response()
        return payload if isinstance(payload, list) else [payload] # making sure to put the response in a list in case it's 1 byte long, and would be returned as an int from get_response(), as a result

    def transmit_payload(self, payload, timeout=4, retransmits=15):
        self.connection.sendall(bytes([TRANSMIT_PAYLOAD, len(payload), timeout, retransmits] + payload)) # like in enter_sniffer_mode
        return self.get_response()

    def set_channel(self, channel):
        self.connection.sendall(bytes([SET_CHANNEL, channel]))
        return self.get_response()

    def get_channel(self):
        self.connection.sendall(bytes([GET_CHANNEL]))
        return self.get_response()

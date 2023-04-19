# constants
UNKNOWN            = 0
LOGI_MOUSE         = 1
LOGI_ENC_KEYSTROKE = 2
LOGI_MULTIMEDIA    = 3
LOGI_SET_TIMEOUT   = 4
LOGI_KEEPALIVE     = 5
MS_ENC_MOUSE       = 6
MS_UNENC_MOUSE     = 7
MS_ENC_KEYSTROKE   = 8

types = {
    UNKNOWN:            "Unknown",
    LOGI_MOUSE:         "Logitech Mouse",
    LOGI_ENC_KEYSTROKE: "Logitech Encrypted Keystroke",
    LOGI_MULTIMEDIA:    "Logitech Multimedia Keystroke",
    LOGI_SET_TIMEOUT:   "Logitech Set Keepalive Timeout",
    LOGI_KEEPALIVE:     "Logitech Keepalive",
    MS_ENC_MOUSE:       "Microsoft Encrypted Mouse",
    MS_UNENC_MOUSE:     "Microsoft Unencrypted Mouse",
    MS_ENC_KEYSTROKE:   "Microsoft Encrypted Keystroke"
}

def identify_type(payload):
    """
    This function receives an RF payload and returns its most likely type.
    """
    if len(payload) == 10 and (payload[0] == 0x00 or payload[0] == 0x08) and payload[1] == 0xC2: # refer to Table 6 in the MouseJack whitepaper: Logitech Mouse Payload
        return LOGI_MOUSE
    elif len(payload) == 22 and payload[0] == 0x00 and payload[1] == 0xD3: # refer to Table 7 in the MouseJack whitepaper: Logitech Encrypted Keystroke Payload
        return LOGI_ENC_KEYSTROKE
    elif len(payload) == 10 and payload[0] == 0x00 and payload[1] == 0xC3: # refer to Table 9 in the MouseJack whitepaper: Logitech Multimedia Key Payload
        return LOGI_MULTIMEDIA
    elif len(payload) == 10 and payload[0] == 0x00 and payload[1] == 0x4F: # refer to Figure 5 in the MouseJack whitepaper: Logitech Unifying Set Keepalive Timeout Payload
        return LOGI_SET_TIMEOUT
    elif len(payload) == 5 and payload[0] == 0x00 and payload[1] == 0x40: # refer to Figure 6 in the MouseJack whitepaper: Logitech Unifying Keepalive Payload
        return LOGI_KEEPALIVE
    elif len(payload) == 19 and payload[0] == 0x0A: # XOR-encrypted Microsoft mouse, deduced by sniffing
        return MS_ENC_MOUSE
    elif len(payload) == 19 and payload[0] == 0x08 and payload[6] == 0x40: # unencrypted Microsoft mouse, deduced by sniffing
        return MS_UNENC_MOUSE
    elif (len(payload) == 20 and (payload[0] == 0x09 or payload[0] == 0x0D) and payload[1] == 0x98) or \
         (len(payload) == 8  and (payload[0] == 0x08 or payload[0] == 0x0C) and payload[1] == 0x38):
        # AES-encrypted Microsoft keyboard, deduced by sniffing and by: https://github.com/samyk/keysweeper/blob/master/keysweeper_mcu_src/keysweeper_mcu_src.ino#L47
        return MS_ENC_KEYSTROKE
    
    return UNKNOWN

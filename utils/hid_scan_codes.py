# refer to: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

# General
KEY_RELEASE = 0x00 # No key pressed

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
KEY_1 = 0x1E # Keyboard 1 and !
KEY_2 = 0x1F # Keyboard 2 and @
KEY_3 = 0x20 # Keyboard 3 and #
KEY_4 = 0x21 # Keyboard 4 and $
KEY_5 = 0x22 # Keyboard 5 and %
KEY_6 = 0x23 # Keyboard 6 and ^
KEY_7 = 0x24 # Keyboard 7 and &
KEY_8 = 0x25 # Keyboard 8 and *
KEY_9 = 0x26 # Keyboard 9 and (
KEY_0 = 0x27 # Keyboard 0 and )

# Useful keys
KEY_ENTER      = 0x28 # Keyboard Return (ENTER)
KEY_ESC        = 0x29 # Keyboard ESCAPE
KEY_BACKSPACE  = 0x2A # Keyboard DELETE (Backspace)
KEY_TAB        = 0x2B # Keyboard Tab
KEY_SPACE      = 0x2C # Keyboard Spacebar
KEY_MINUS      = 0x2D # Keyboard - and _
KEY_EQUAL      = 0x2E # Keyboard = and +
KEY_LEFTBRACE  = 0x2F # Keyboard [ and {
KEY_RIGHTBRACE = 0x30 # Keyboard ] and }
KEY_BACKSLASH  = 0x31 # Keyboard \ and |
KEY_HASHTILDE  = 0x32 # Keyboard Non-US # and ~
KEY_SEMICOLON  = 0x33 # Keyboard ; and :
KEY_APOSTROPHE = 0x34 # Keyboard ' and "
KEY_GRAVE      = 0x35 # Keyboard ` and ~
KEY_COMMA      = 0x36 # Keyboard , and <
KEY_DOT        = 0x37 # Keyboard . and >
KEY_SLASH      = 0x38 # Keyboard / and ?
KEY_CAPSLOCK   = 0x39 # Keyboard Caps Lock

# F-keys
KEY_F1  = 0x3A # Keyboard F1
KEY_F2  = 0x3B # Keyboard F2
KEY_F3  = 0x3C # Keyboard F3
KEY_F4  = 0x3D # Keyboard F4
KEY_F5  = 0x3E # Keyboard F5
KEY_F6  = 0x3F # Keyboard F6
KEY_F7  = 0x40 # Keyboard F7
KEY_F8  = 0x41 # Keyboard F8
KEY_F9  = 0x42 # Keyboard F9
KEY_F10 = 0x43 # Keyboard F10
KEY_F11 = 0x44 # Keyboard F11
KEY_F12 = 0x45 # Keyboard F12

KEY_SYSRQ      = 0x46 # Keyboard Print Screen
KEY_SCROLLLOCK = 0x47 # Keyboard Scroll Lock
KEY_PAUSE      = 0x48 # Keyboard Pause
KEY_INSERT     = 0x49 # Keyboard Insert
KEY_HOME       = 0x4A # Keyboard Home
KEY_PAGEUP     = 0x4B # Keyboard Page Up
KEY_DELETE     = 0x4C # Keyboard Delete Forward
KEY_END        = 0x4D # Keyboard End
KEY_PAGEDOWN   = 0x4E # Keyboard Page Down
KEY_RIGHT      = 0x4F # Keyboard Right Arrow
KEY_LEFT       = 0x50 # Keyboard Left Arrow
KEY_DOWN       = 0x51 # Keyboard Down Arrow
KEY_UP         = 0x52 # Keyboard Up Arrow

# Multimedia keys for Logitech keyboards (Based on page 126 here: https://www.usb.org/sites/default/files/hut1_4.pdf)
KEY_FN_F1  = 0x223 # Launch Web browser
KEY_FN_F2  = 0x18A # Launch Email application
KEY_FN_F3  = 0x221 # Search
KEY_FN_F4  = 0x192 # Launch calculator
KEY_FN_F5  = 0x183 # Launch media player
KEY_FN_F6  = 0xB6  # Prev Track
KEY_FN_F7  = 0xCD  # Play/Pause Track
KEY_FN_F8  = 0xB5  # Next Track
KEY_FN_F9  = 0xE2  # Mute
KEY_FN_F10 = 0xEA  # Volume down
KEY_FN_F11 = 0xE9  # Volume up
KEY_FN_F12 = 0x46  # Print screen (this is actually not a multimedia key at all, since it generates the same code as the standard Print Screen key)

# putting these values in a list so that one can quickly test whether a given key is a multimedia key
multimedia_keys = [KEY_FN_F1, KEY_FN_F2, KEY_FN_F3, KEY_FN_F4, KEY_FN_F5, KEY_FN_F6, KEY_FN_F7, KEY_FN_F8, KEY_FN_F9, KEY_FN_F10, KEY_FN_F11, KEY_FN_F12]

# dictionary for general functions:
# TODO: add shift clicking in the right cases
letters_dict = {
    'a': KEY_A,
    'A': KEY_A,
    'b': KEY_B,
    'B': KEY_B,
    'c': KEY_C,
    'C': KEY_C,
    'd': KEY_D,
    'D': KEY_D,
    'e': KEY_E,
    'E': KEY_E,
    'f': KEY_F,
    'F': KEY_F,
    'g': KEY_G,
    'G': KEY_G,
    'h': KEY_H,
    'H': KEY_H,
    'i': KEY_I,
    'I': KEY_I,
    'j': KEY_J,
    'J': KEY_J,
    'k': KEY_K,
    'K': KEY_K,
    'l': KEY_L,
    'L': KEY_L,
    'm': KEY_M,
    'M': KEY_M,
    'n': KEY_N,
    'N': KEY_N,
    'o': KEY_O,
    'O': KEY_O,
    'p': KEY_P,
    'P': KEY_P,
    'q': KEY_Q,
    'Q': KEY_Q,
    'r': KEY_R,
    'R': KEY_R,
    's': KEY_S,
    'S': KEY_S,
    't': KEY_T,
    'T': KEY_T,
    'u': KEY_U,
    'U': KEY_U,
    'v': KEY_V,
    'V': KEY_V,
    'w': KEY_W,
    'W': KEY_W,
    'x': KEY_X,
    'X': KEY_X,
    'y': KEY_Y,
    'Y': KEY_Y,
    'z': KEY_Z,
    'Z': KEY_Z,
    '1': KEY_1,
    '!': KEY_1,
    '2': KEY_2,
    '@': KEY_2,
    '3': KEY_3,
    '#': KEY_3,
    '4': KEY_4,
    '$': KEY_4,
    '5': KEY_5,
    '%': KEY_5,
    '6': KEY_6,
    '^': KEY_6,
    '7': KEY_7,
    '&': KEY_7,
    '8': KEY_8,
    '*': KEY_8,
    '9': KEY_9,
    '(': KEY_9,
    '0': KEY_0,
    ')': KEY_0,
    '\n': KEY_ENTER,
    '\x1b': KEY_ESC,
    '\x08': KEY_BACKSPACE,
    '\t': KEY_TAB,
    ' ': KEY_SPACE,
    '-': KEY_MINUS,
    '_': KEY_MINUS,
    '=': KEY_EQUAL,
    '+': KEY_EQUAL,
    '[': KEY_LEFTBRACE,
    '{': KEY_LEFTBRACE,
    ']': KEY_RIGHTBRACE,
    '}': KEY_RIGHTBRACE,
    '\\': KEY_BACKSLASH,
    '|': KEY_BACKSLASH,
    ';': KEY_SEMICOLON,
    ':': KEY_SEMICOLON,
    "'": KEY_APOSTROPHE,
    '"': KEY_APOSTROPHE,
    ',': KEY_COMMA,
    '<': KEY_COMMA,
    '.': KEY_DOT,
    '>': KEY_DOT,
    '/': KEY_SLASH,
    '?': KEY_SLASH,
    '`': KEY_GRAVE,
    '~': KEY_GRAVE
}

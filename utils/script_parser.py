from .general_utils import *
from .hid_scan_codes import *
from .vendors import logitech

def parse_script_file(radio, filename, vendor=logitech):
    """
    Parses a Ducky-like script from a file and executes it.

    Parameters:
    filename (str): The name of the file containing the script.

    Raises:
    ValueError: If the script contains an unknown command.

    """
    with open(filename, 'r') as f:
        script = f.read()
        parse_script(radio, script, vendor)

def parse_script(radio, script, vendor=logitech):
    """
    Parses a Ducky-like script and executes it.

    Parameters:
    script (str): The Ducky-like script to parse and execute.

    Raises:
    ValueError: If the script contains an unknown command.
    """
    for line in script.split('\n'):
        if not line.strip(): # ignore empty lines
            continue
        parts = line.split()
        if len(parts) == 0:
            continue
        command = parts[0]
        args = parts[1:]
        if command == 'REM':
            continue
        elif command == 'WINDOWS':
            if args:
                scan_code = other_keys[args[0]][0]
            else:
                scan_code = KEY_NONE
            inject_keystrokes(radio, [[scan_code, KEY_MOD_LMETA]], vendor)
        elif command == 'STRING':
            transmit_string(radio, ' '.join(args), vendor)
        elif command == 'DELAY':
            # patch: treating DELAY as a "keystroke" passed to inject_keystrokes(), by using a custom scan code defined for this purpose, and passing the interval (in ms) through the modifier
            inject_keystrokes(radio, [[KEY_DELAY, int(args[0])]], vendor)
        elif command == 'CTRL-SHIFT':
            inject_keystrokes(radio, [[other_keys[args[0]][0], KEY_MOD_LCTRL | KEY_MOD_RSHIFT]], vendor)
        elif command in other_keys.keys():
            transmit_keys(radio, [command], vendor)
        else:
            raise ValueError(f'Unknown command: {command}')

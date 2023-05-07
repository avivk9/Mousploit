from .general_utils import *
from .hid_scan_codes import *
from . import logitech

def parse_script_file(radio, filename):
    """
    Parses a Ducky-like script from a file and executes it.

    Parameters:
    filename (str): The name of the file containing the script.

    Raises:
    ValueError: If the script contains an unknown command.

    """
    with open(filename, 'r') as f:
        script = f.read()
        parse_script(radio, script)

def parse_script(radio, script):
    """
    Parses a Ducky-like script and executes it.

    Parameters:
    script (str): The Ducky-like script to parse and execute.

    Raises:
    ValueError: If the script contains an unknown command.
    """
    for line in script.split('\n'):
        parts = line.split()
        if len(parts) == 0:
            continue
        command = parts[0]
        args = parts[1:]
        if command == 'REM':
            print(' '.join(args))
        elif command == 'WINDOWS':
            transmit_keys(radio, [command])
        elif command == 'STRING':
            transmit_string(radio, ' '.join(args))
        elif command == 'DELAY':
            # patch: treating DELAY as a "keystroke" passed to inject_keystrokes(), by using a custom scan code defined for this purpose, and passing the interval (in ms) through the modifier
            logitech.inject_keystrokes(radio, [[KEY_DELAY, int(args[0])]])
        elif command == 'ENTER':
            transmit_keys(radio, [command])
        elif command == 'CTRL-SHIFT' and args[0] == 'ENTER':
            transmit_keys(radio, ['CTRL', 'SHIFT', 'ENTER'])
        elif command == 'ALT' and args[0] == 'y':
            transmit_keys(radio, ['ALT', 'y'])
        else:
            raise ValueError(f'Unknown command: {command}')

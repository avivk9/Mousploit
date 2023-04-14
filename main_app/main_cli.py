"""
The Mousploit CLI works by executing mousploit.py with command line arguments corresponding to the selections made by the user.
"""

import colorama
from colorama import Fore, Style
import sys
import os

colorama.init(autoreset=True)

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

    print("Mousploit - Proof of Concept")
    print("Team: Ron Greenberg, Aviv Keinan, Itamar Azmoni, Yonatan Birman")

# this function prints the options for the user to choose from
def print_options():
    print("""
Choose an option:
'1' - Scan for nearby vulnerable devices.
'2' - Perform a keystroke injection attack against a specified target.
'3' - Exit.""")

def main():
    print_logo()
    print_options()

    while True:
        selection = input("> ") # getting input from the user
        cmd = "python mousploit.py " # beginning of command that executes mousploit.py
        
        # if the user chooses to scan
        if selection == "1":
            cmd += "scan "
            duration = input("Enter scan duration in seconds (leave blank to use default): ")
            if duration == "":
                print("Using default duration: 20 seconds")
            else:
                cmd += f"--duration {duration}" # adding the proper argument to the command string

        # if the user chooses to attack
        elif selection == "2":
            cmd += "attack "
            address = input("Enter address (leave blank to use default): ")
            if address == "":
                print("Using default address: E4:ED:AE:B8:B4")
            else:
                cmd += f"--address {address} "
            option = input("Select injection type ('1' - string, '2' - DuckyScript, '3' - From your keyboard to victim keyboard): ")
            if option == '1': # inject string
                string = input("Enter string: ")
                cmd += f"--string \"{string}\"" # if the string contains whitespaces, it must be surrounded with DOUBLE quotes
            elif option == '2': # inject DuckyScript
                path = input("Enter path of DuckyScript file: ")
                cmd += f"--script-file \"{path}\""
            elif option == '3':
                cmd += f"--keyboard-live"

        # if the user chooses to exit
        elif selection == "3":
            print("bye!")
            sys.exit(0)

        # if the user types anything else, continue to prompt for input (without printing options again)
        else:
            continue
        
        os.system(cmd) # execute the command in a subshell (just like the system() function in C)
        print_options() # print the options for next round

if __name__ == '__main__':
    main()

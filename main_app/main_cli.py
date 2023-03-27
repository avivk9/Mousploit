import colorama
from colorama import Fore, Style
import sys
import os

colorama.init(autoreset=True)

def print_help():
    print("""
        Choose an option:
        '1' - Perform a keystroke injection attack against a specified target.
        '2' - Scan for nearby vulnerable devices.
        '3' - Exit.
          """)

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
    #print("Final Project in Cyber Security - College of Management")
    print("Team: Ron Greenberg, Aviv Keinan, Itamar Azmoni, Yonatan Birman\n")

def main():
    print_logo()
    while True:
        print_help() # print options
        request = input("> ")
        
        cmd = "python mousploit.py "
        if request == "1": # in case of attack
            address = input("Enter address")
            if address != "":
                cmd += f"--address {address} "
            opt = input("""
                        Enter '1' for string.
                        Enter '2' for script.""")
            if opt == '1': # inject string
                string = input("Enter string")
                cmd += f"--string \"{string}\""
            elif opt == '2': # inject duckyscript
                path = input("Enter path of duckyscript file")
                cmd += f"--script-file \"{path}\""

        elif request == "2": # in case of scan
            duration = input("Enter duration")
            cmd += f"scan --duration {duration}"

        elif request == "3": # in case of exit
            print("bye!")
            sys.exit()

        os.system(cmd)

if __name__ == '__main__':
    main()

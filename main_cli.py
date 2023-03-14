import colorama
from colorama import Fore, Style
from mousejack.mousejack import *

colorama.init(autoreset=True)


def print_help():
    print("helping")
    pass

def print_logo():
    # Print the headline with colorized text
    # print(f'{Fore.GREEN}\
    # _      ____  _     ____  ____  _     ____  _  _____    \n\
    # / \__/|/  _ \/ \ /\/ ___\/  __\/ \   /  _ \/ \/__ __\   \n\
    # | |\/||| / \|| | |||    \|  \/|| |   | / \|| |  / \     \n\
    # | |  ||| \_/|| \_/|\___ ||  __/| |_/\| \_/|| |  | |     \n\
    # \_/  \|\____/\____/\____/\_/   \____/\____/\_/  \_/     \n\
    # ')

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
    print("for help use 'help', to exit use 'exit'")


def main():
    print_logo()
    while True:
        request = input("> ")
        
        if request.__contains__('exit'):
            print("bye!")
            break
        
        if request.__contains__('help'):
            print_help()
            continue
        
        # example - TODO: CHANGE
        if request.__contains__('scan'):
            MouseJack.scan()
            continue
        


        # anything else:
        print('what do u mean?')

if __name__ == '__main__':
    main()

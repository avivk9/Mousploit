import colorama
from colorama import Fore, Style
from mousejack.mousejack import *

colorama.init(autoreset=True)


def print_help():
    print("helping")
    pass

def setup():
    """initial prints and ect"""
    # Print the headline with colorized text
    print(f'{Fore.GREEN}\
    _      ____  _     ____  ____  _     ____  _  _____    \n\
    / \__/|/  _ \/ \ /\/ ___\/  __\/ \   /  _ \/ \/__ __\   \n\
    | |\/||| / \|| | |||    \|  \/|| |   | / \|| |  / \     \n\
    | |  ||| \_/|| \_/|\___ ||  __/| |_/\| \_/|| |  | |     \n\
    \_/  \|\____/\____/\____/\_/   \____/\____/\_/  \_/     \n\
    ')

    print(f"Final project at cyber security at the college of management\n")
    print(f"for help use 'help', to exit use 'exit'\n")


def main():
    setup()
    while True:
        request = input("> ")
        
        if request.__contains__('exit'):
            print("bye !")
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

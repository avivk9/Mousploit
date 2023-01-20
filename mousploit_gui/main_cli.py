import colorama
from colorama import Fore

colorama.init(autoreset=True)


def print_help():
    print("helping")
    pass





print(f"~Welcom to {Fore.GREEN}Mousploit")
print(f"Final project at cyber security at the college of management\n")
print(f"for help use 'help', to exit use 'exit'\n")

while True:
    request = input("> ")
    if request.__contains__('exit'):
        print("bye !")
        break
    if request.__contains__('help'):
        print_help()


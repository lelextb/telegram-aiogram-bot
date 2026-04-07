import sys
sys.path.append("..")
from bot.handlers.commands import process_command

def main():
    data = sys.stdin.read()
    process_command(data)

if __name__ == "__main__":
    main()
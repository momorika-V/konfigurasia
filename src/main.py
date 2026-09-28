"""Эмулятор оболочки ОС. Этап 1: REPL."""
import os
import sys
import shlex
import getpass
import socket

def make_prompt() -> str:
    username = getpass.getuser()
    hostname = socket.gethostname()
    cwd = os.getcwd()
    home = os.path.expanduser("~")

    if cwd == home:
        path = "~"
    elif cwd.startswith(home + os.sep):
        path = "~" + cwd[len(home):]
    else:
        path = cwd

    return f"{username}@{hostname}:{path}$ "


def expand_line(line: str) -> str:
    return os.path.expandvars(line)


def parse_line(line: str) -> list:
    try:
        return shlex.split(line)
    except ValueError as e:
        print(f"parse error: {e}")
        return []


def expand_tilde(args: list) -> list:
    new_args = []

    for a in args:
        if a.startswith("~"):
            a = os.path.expanduser(a)
        new_args.append(a)

    return new_args


def cmd_ls(args: list) -> None:
    print(f"ls: stub, arguments: {args}")


def cmd_cd(args: list) -> None:
    print(f"cd: stub, arguments: {args}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
}


def main() -> int:
    print("OS shell emulator. Type exit to quit.")
    while True:
        try:
            line = input(make_prompt())
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        line = expand_line(line)
        tokens = parse_line(line)
        if not tokens:
            continue

        cmd = tokens[0]
        args = tokens[1:]
        args = expand_tilde(args)

        if cmd == "exit":
            break
        elif cmd in COMMANDS:
            COMMANDS[cmd](args)
        else:
            print(f"{cmd}: command not found")
    return 0


if __name__ == "__main__":
    sys.exit(main())

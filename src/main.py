"""Эмулятор оболочки ОС. Этап 2: конфигурация."""

import argparse
import getpass
import os
import shlex
import socket
import sys
from typing import Optional

STATUS_OK = 0
STATUS_ERROR = 1
STATUS_EXIT = 2


def make_prompt(custom_prompt: Optional[str]) -> str:
    """Возвращает приглашение к вводу (своё или по данным ОС)."""
    if custom_prompt:
        return custom_prompt

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
    """Раскрывает переменные окружения реальной ОС в строке."""
    return os.path.expandvars(line)


def parse_line(line: str) -> Optional[list]:
    """Разбивает строку на команду и аргументы.

    Возвращает None при ошибке разбора (незакрытые кавычки).
    """
    try:
        return shlex.split(line)
    except ValueError as e:
        print(f"parse error: {e}")
        return None


def expand_tilde(args: list) -> list:
    """Раскрывает '~' в начале аргументов."""
    new_args = []
    for a in args:
        if a.startswith("~"):
            a = os.path.expanduser(a)
        new_args.append(a)
    return new_args


def cmd_ls(args: list) -> None:
    """Заглушка команды ls: выводит имя и аргументы."""
    print(f"ls: stub, arguments: {args}")


def cmd_cd(args: list) -> None:
    """Заглушка команды cd: выводит имя и аргументы."""
    print(f"cd: stub, arguments: {args}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
}


def dispatch(line: str) -> int:
    """Выполняет одну строку ввода.

    Возвращает STATUS_OK при успехе, STATUS_ERROR при ошибке,
    STATUS_EXIT при команде exit.
    """
    line = expand_line(line)
    tokens = parse_line(line)
    if tokens is None:
        return STATUS_ERROR
    if not tokens:
        return STATUS_OK

    cmd = tokens[0]
    args = expand_tilde(tokens[1:])

    if cmd == "exit":
        return STATUS_EXIT
    if cmd in COMMANDS:
        COMMANDS[cmd](args)
        return STATUS_OK

    print(f"{cmd}: command not found")
    return STATUS_ERROR


def parse_args(argv: list) -> argparse.Namespace:
    """Разбирает параметры командной строки эмулятора."""
    parser = argparse.ArgumentParser(prog="emulator")
    parser.add_argument("--vfs", default=None, help="path to VFS")
    parser.add_argument("--prompt", default=None, help="custom prompt")
    parser.add_argument("--script", default=None, help="startup script")
    return parser.parse_args(argv)


def run_interactive(cfg: argparse.Namespace) -> int:
    """Запускает интерактивный режим REPL."""
    print("OS shell emulator. Type exit to quit.")
    prompt = make_prompt(cfg.prompt)

    while True:
        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        if dispatch(line) == STATUS_EXIT:
            break

    return STATUS_OK


def read_script(path: str) -> Optional[list]:
    """Читает строки скрипта или сообщает об ошибке открытия."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.readlines()
    except OSError as e:
        print(f"script error: cannot open {path}: {e}")
        return None


def run_script(cfg: argparse.Namespace) -> int:
    """Выполняет стартовый скрипт, останавливаясь при первой ошибке."""
    lines = read_script(cfg.script)
    if lines is None:
        return STATUS_ERROR

    prompt = make_prompt(cfg.prompt)

    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        print(prompt + line)
        status = dispatch(line)
        if status == STATUS_ERROR:
            print(f"script error: stopped at line: {line}")
            return STATUS_ERROR
        if status == STATUS_EXIT:
            break

    return STATUS_OK


def main(argv: list) -> int:
    """Точка входа: выбирает режим работы эмулятора."""
    cfg = parse_args(argv)

    if cfg.script:
        return run_script(cfg)
    return run_interactive(cfg)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
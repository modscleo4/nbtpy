# A Python 3 NBT (Named Binary Tag) Parser
#
# Copyright 2021 Dhiego Cassiano Fogaça Barbosa <modscleo4@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys


__version__ = '0.0.1'


class COLORS:
    reset: int = 0
    bold: int = 1
    underline: int = 4
    blink: int = 5
    reverse: int = 7
    hidden: int = 8
    black: int = 30
    red: int = 31
    green: int = 32
    yellow: int = 33
    blue: int = 34
    magenta: int = 35
    cyan: int = 36
    white: int = 37
    bright_black: int = 90
    bright_red: int = 91
    bright_green: int = 92
    bright_yellow: int = 93
    bright_blue: int = 94
    bright_magenta: int = 95
    bright_cyan: int = 96
    bright_white: int = 97


def remove_version_constraint(pkg):
    '''
    Remove version constraint from package name.
    '''
    match = re.search('^[^<>=!]*', pkg)
    return match.group() if match else ''


def color_text(text: str, color: int):
    '''
    Return a colored text using ASCII escape sequences.
    '''
    return f"\033[{color}m{text}\033[{COLORS.reset}m"


def prompt(text: str, default: str = 'y') -> bool:
    '''
    Print a [y/n] prompt.
    '''
    result = input(f" {color_text('::', COLORS.blue)} {text} [{'Y/n' if default == 'y' else 'y/N'}]: ").lower()
    result = result if result else default
    return result == 'y'


def info(text: str, file=sys.stdout) -> None:
    '''
    Print an info message.
    '''
    print(f"{color_text('==>', COLORS.green)} {text}", file=file)


def warning(text: str, file=sys.stdout) -> None:
    '''
    Print a warning message.
    '''
    print(f"{color_text('==>', COLORS.bright_yellow)} {text}", file=file)


def error(text: str, file=sys.stderr) -> None:
    '''
    Print an error message.
    '''
    print(f"{color_text('==>', COLORS.red)} {text}", file=file)

import os
import sys
import tty, termios
import string
import shutil
from .charDef import *
from . import colors

COLUMNS, _ = shutil.get_terminal_size()  ## Size of console

def mygetc():
    ''' Get raw characters from input. '''
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def getchar():
    ''' Character input parser. '''
    c = mygetc()
    if ord(c) == LINE_BEGIN_KEY or \
       ord(c) == LINE_END_KEY   or \
       ord(c) == TAB_KEY        or \
       ord(c) == INTERRUPT_KEY  or \
       ord(c) == NEWLINE_KEY:
       return c
    
    elif ord(c) == BACK_SPACE_KEY:
        return c
    
    elif ord(c) == ESC_KEY:
        combo = mygetc()
        if ord(combo) == MOD_KEY_INT:
            key = mygetc()
            if ord(key) >= MOD_KEY_BEGIN - MOD_KEY_FLAG and ord(key) <= MOD_KEY_END - MOD_KEY_FLAG:
                if ord(mygetc()) == MOD_KEY_DUMMY:
                    return chr(ord(key) + MOD_KEY_FLAG)
                else:
                    return UNDEFINED_KEY
            elif ord(key) >= ARROW_KEY_BEGIN - ARROW_KEY_FLAG and ord(key) <= ARROW_KEY_END - ARROW_KEY_FLAG:
                return chr(ord(key) + ARROW_KEY_FLAG)
            else:
                return UNDEFINED_KEY
        else:
            return getchar()

    else:
        if is_printable(c):
            return c
        else:
            return UNDEFINED_KEY

    return UNDEFINED_KEY

# Basic command line functions

def moveCursorLeft(n):
    ''' Move cursor left n columns. '''
    forceWrite("\033[{}D".format(n))

def moveCursorRight(n):
    ''' Move cursor right n columns. '''
    forceWrite("\033[{}C".format(n))
    
def moveCursorUp(n):
    ''' Move cursor up n rows. '''
    forceWrite("\033[{}A".format(n))

def moveCursorDown(n):
    ''' Move cursor down n rows. '''
    forceWrite("\033[{}B".format(n))

def moveCursorHead():
    ''' Move cursor to the start of line. '''
    forceWrite("\r")

def clearLine():
    ''' Clear content of one line on the console. '''
    forceWrite(" " * COLUMNS)
    moveCursorHead()
    
def clearConsoleUp(n):
    ''' Clear n console rows (bottom up). ''' 
    for _ in range(n):
        clearLine()
        moveCursorUp(1)

def clearConsoleDown(n):
    ''' Clear n console rows (top down). ''' 
    for _ in range(n):
        clearLine()
        moveCursorDown(1)
    moveCursorUp(n)

def forceWrite(s, end = ''):
    ''' Dump everthing in the buffer to the console. '''
    sys.stdout.write(s + end)
    sys.stdout.flush()

def cprint(
        s: str, 
        color: str = colors.foreground["default"], 
        on: str = colors.background["default"], 
        end: str = '\n'
    ):
    ''' Colored print function.
    Args:
        s: The string to be printed.
        color: The color of the string.
        on: The color of the background.
        end: Last character appended. 
    Returns:
        None
    '''
    forceWrite(on + color + s + colors.RESET, end = end)

def is_printable(s: str) -> bool:
    """Determine if a string contains only printable characters.
    Args:
        s: The string to verify.
    Returns:
        bool: `True` if all characters in `s` are printable. `False` if any
            characters in `s` can not be printed.
    """
    # Ref: https://stackoverflow.com/a/50731077
    return not any(repr(ch).startswith(("'\\x", "'\\u")) for ch in s)
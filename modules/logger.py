import colorama
from enum import Enum
import sys
import datetime

colorama.just_fix_windows_console()

class LogLevel(Enum):
    NORMAL = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    SUCCESS = 4

_COLORS = {
    LogLevel.NORMAL: colorama.Fore.LIGHTBLUE_EX,
    LogLevel.INFO: colorama.Fore.LIGHTGREEN_EX,
    LogLevel.WARN: colorama.Fore.YELLOW,
    LogLevel.ERROR:  colorama.Fore.RED,
    LogLevel.SUCCESS: colorama.Fore.GREEN
}

def log(log_level: LogLevel, fmt: str):
    color = _COLORS[log_level]
    stream = sys.stderr if log_level == LogLevel.ERROR else sys.stdout
    now = datetime.datetime.now().replace(microsecond=0)

    if log_level != LogLevel.NORMAL:
        print(
            f"{colorama.Fore.BLUE}{now}:{colorama.Style.RESET_ALL} "
            f"{color}[{log_level.name}]{colorama.Style.RESET_ALL} {fmt}",
            file=stream
        )
    else:
        print(
            f"{colorama.Fore.BLUE}{now}:{colorama.Style.RESET_ALL} "
            f"{color}{fmt}{colorama.Style.RESET_ALL}",
            file=stream
        )

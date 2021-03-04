import ctypes
import collections
from ctypes import wintypes
import argparse

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

HISTORY_NO_DUP_FLAG = 1

class CONSOLE_HISTORY_INFO(ctypes.Structure):
    _fields_ = (('cbSize', wintypes.UINT),
                ('HistoryBufferSize', wintypes.UINT),
                ('NumberOfHistoryBuffers', wintypes.UINT),
                ('dwFlags', wintypes.DWORD))

    def __init__(self, *args, **kwds):
        super().__init__(ctypes.sizeof(self), *args, **kwds)

ConsoleHistoryInfo = collections.namedtuple('ConsoleHistoryInfo', 
    'bufsize nbuf flags')

def get_console_history_info():
    info = CONSOLE_HISTORY_INFO()
    if not kernel32.GetConsoleHistoryInfo(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return ConsoleHistoryInfo(info.HistoryBufferSize, 
            info.NumberOfHistoryBuffers, info.dwFlags)

def set_console_history_info(bufsize=512, nbuf=32,
      flags=HISTORY_NO_DUP_FLAG):
    info = CONSOLE_HISTORY_INFO(bufsize, nbuf, flags)
    if not kernel32.SetConsoleHistoryInfo(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--set", action="store_true", help="Set the configuration values")
    p.add_argument("--size", type=int, default=512, help="Set the buffer size [default 512]")
    p.add_argument("--nbuf", type=int, default=32, help="Set the number of buffers [default 32]")
    p.add_argument("--discard-duplicates", action="store_true", help="Discard old duplicates [default no]")
    p.add_argument("--quiet", "-q", action="store_true", help="Set the configuration values")
    args = p.parse_args()
    if args.set:
        set_console_history_info(args.size, args.nbuf, flags=(HISTORY_NO_DUP_FLAG if args.discard_duplicates else 0))

    if not (args.set and args.quiet):
        info = get_console_history_info()
        print(f"Buffers: {info.nbuf}, Size: {info.bufsize}, Discard duplicates: {'yes' if info.flags else 'no'}")

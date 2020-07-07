import sys

LINUX = (sys.platform == 'linux' or sys.platform == 'linux2')
WINDOWS = (sys.platform == 'win32' or sys.platform == 'win64')
FREEBSD = ('freebsd' in sys.platform)
UNIX = LINUX or FREEBSD
INTEGER_TYPES = int,

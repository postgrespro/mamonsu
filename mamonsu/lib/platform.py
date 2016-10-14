import sys

LINUX = (sys.platform == 'linux' or sys.platform == 'linux2')
WINDOWS = (sys.platform == 'win32' or sys.platform == 'win64')
FREEBSD = ('freebsd' in sys.platform)
UNIX = LINUX or FREEBSD

PY2 = (sys.version_info[0] == 2)
PY3 = (sys.version_info[0] == 3)

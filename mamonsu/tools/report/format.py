# -*- coding: utf-8 -*-

import re
import sys
import mamonsu.lib.platform as platform


class color(object):

    mapping = {
        'BOLD': '\033[0;0m\033[1;1m',
        'RED': '\033[1;31m',
        'GRAY': '\033[1;30m',
        'PURPLE': '\033[1;35m',
        'BLUE': '\033[1;34m',
        'END': '\033[1;m'
    }

    def __init__(self):
        self.color = sys.stdout.isatty()

    def disable(self):
        self.color = False

    def __getattr__(self, name):
        if self.color:
            return self.mapping[name]
        else:
            return ''


TermColor = color()


# int (bytes) => str (human readable)
def humansize_bytes(nbytes):
    fmt = '{0:>6} {1}'
    if not isinstance(nbytes, platform.INTEGER_TYPES):
        return 'ERROR'
    if nbytes == 0:
        return fmt.format(0, 'B')
    i, suffixes, = 0, ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return fmt.format(f, suffixes[i])


# str (some formates) => str (human readable)
def humansize(value):
    m = re.search('(\d+) (\S+)', value)
    if m is None:
        return value
    val, suff = m.group(1), m.group(2)
    val, suff = int(val), suff.upper()
    if suff == 'S':
        return value
    if suff == 'MS':
        return value
    if suff == 'B':
        return humansize_bytes(val)
    if suff == 'KB':
        return humansize_bytes(val * 1024)
    if suff == '4KB':
        return humansize_bytes(val * 1024 * 4)
    if suff == '8KB':
        return humansize_bytes(val * 1024 * 8)
    if suff == '16KB':
        return humansize_bytes(val * 1024 * 16)
    if suff == 'MB':
        return humansize_bytes(val * 1024 * 1024)
    if suff == 'GB':
        return humansize_bytes(val * 1024 * 1024 * 1024)
    if suff == 'TB':
        return humansize_bytes(val * 1024 * 1024 * 1024 * 1024)
    return value


def header_h1(info):
    return "\n{0}{1}{2}{3}\n".format(
        TermColor.BOLD, TermColor.RED, info.upper(), TermColor.END)


def key_val_h1(key, val, spaces=12):
    fmt = "  {0}{1}{2:" + str(spaces) + "}{3}: {4}\n"
    return fmt.format(
        TermColor.BOLD, TermColor.PURPLE, key, TermColor.END, val)


def header_h2(info):
    return "  {0}{1}{2}{3}\n".format(
        TermColor.BOLD, TermColor.PURPLE, info, TermColor.END)


def key_val_h2(key, val, delim=': '):
    return "    {0}{1}{2:4}{3}{4}{5}\n".format(
        TermColor.BOLD, TermColor.BLUE, key, TermColor.END, delim, val)


def topline_h1(arr=[], delim="  \t"):
    result = "{0}{1}".format(TermColor.BOLD, TermColor.BLUE)
    for x in arr:
        result = "{0}{1}{2}".format(result, delim, x)
    return "{0}{1}\n".format(result, TermColor.END)


def format_raw_h1(raw=""):
    result = []
    for i, line in enumerate(raw.split("\n")):
        if i == 0:
            result.append("  {0}{1}{2}{3}".format(
                TermColor.BOLD, TermColor.BLUE, line, TermColor.END))
        else:
            result.append("  {0}".format(line))
    return "\n".join(result) + "\n"

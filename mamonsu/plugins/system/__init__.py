import mamonsu.lib.platform as platform


if platform.LINUX:
    __import__('mamonsu.plugins.system.linux')
if platform.WINDOWS:
    __import__('mamonsu.plugins.system.windows')

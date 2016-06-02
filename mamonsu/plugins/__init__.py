import mamonsu.lib.platform as platform

__import__('mamonsu.plugins.common')
__import__('mamonsu.plugins.pgsql')
if platform.LINUX:
    __import__('mamonsu.plugins.linux')
if platform.WINDOWS:
    __import__('mamonsu.plugins.windows')

import mamonsu.lib.platform as platform


class Loader(object):

    @staticmethod
    def load():
        if platform.LINUX:
            __import__('mamonsu.plugins.linux')
        if platform.WINDOWS:
            __import__('mamonsu.plugins.windows')
        __import__('mamonsu.plugins.pgsql')

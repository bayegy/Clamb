import sys


class ProgressBar(object):
    """docstring for progressBar"""

    def __init__(self, amount):
        self.amount = amount
        self.__done=0

    def progress(self, progress):
        self.__done=progress
        perctg = 100 * progress / self.amount
        done = int(50 * progress / self.amount)
        sys.stdout.write("\r[%s%s] %.3f%%\r" % ('█' * done, ' ' * (50 - done), perctg))
        sys.stdout.flush()

    def move(self):
        self.__done += 1
        self.progress(self.__done)

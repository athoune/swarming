from subprocess import Popen, PIPE


class Action(object):
    popen = None

    def start(self):
        pass

    def read(self):
        pass

    def lazy_start(self):
        if self.popen is None:
            self.popen = Popen(self.start(), stdout=PIPE)

    def poll(self):
        if self.popen.poll():
            return None
        result = self.read()
        self.popen = None
        return result


class Ping(Action):

    def __init__(self, target):
        self.target = target

    def start(self):
        return ['ping', '-c', '10', self.target]

    def read(self):
        return self.popen.stdout.readlines()[-1][:-1]

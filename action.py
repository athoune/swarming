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

    def __init__(self, *targets):
        self.targets = targets
        self.n = -1

    def start(self):
        self.n += 1
        if self.n +1 > len(self.targets):
            self.n = 0
        self.args = self.targets[self.n]
        return ['ping', '-c', '10', self.targets[self.n]]

    def read(self):
        return self.args, self.popen.stdout.readlines()[-1][:-1]

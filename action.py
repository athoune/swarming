from subprocess import Popen, PIPE
import time
import re


PACKET_LOSS = re.compile(r".* ([\d.]+)% packet loss.*")
# round-trip min/avg/max/stddev = 366.381/377.219/421.605/15.761 ms
ROUND_TRIP = re.compile(r"(round-trip|rtt) min/avg/max/(std|m)dev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms")


class Action(object):
    popen = None
    tick = 0

    def start(self):
        pass

    def read(self):
        pass

    def lazy_start(self):
        if self.popen is None:
            now = time.time()
            if now - self.tick > 10:
                self.tick = now
                self.popen = Popen(self.start(), stdout=PIPE, stderr=PIPE)

    def poll(self):
        if self.popen is None:
            return None
        if self.popen.poll():
            return None
        result = self.read()
        self.popen = None
        return result


class ActionException(Exception):
    pass


class Ping(Action):

    def __init__(self, *targets):
        self.targets = targets
        self.n = -1

    def start(self):
        self.n += 1
        if self.n + 1 > len(self.targets):
            self.n = 0
        self.args = self.targets[self.n]
        return ['ping', '-c', '10', self.targets[self.n]]

    def read(self):
        try:
            r = parse_ping(self.popen.stderr, self.popen.stdout)
        except ActionException as e:
            return 'error', self.args, str(e)
        return 'ok', self.args, r


def parse_ping(err, out):
    error = err.read()
    if error != '':
        raise ActionException(error[:-1])
    response = {}
    for line in out.readlines()[-2:]:
        m = PACKET_LOSS.match(line)
        if m:
            response['loss'] = float(m.group(1))
        m = ROUND_TRIP.match(line)
        if m:
            response['Round trip'] = [float(a) for a in m.group(3, 4, 5, 6)]
    return response

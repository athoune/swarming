import mosquitto
import socket
import random
import json
import sys

from action import Ping


class MetaClient(object):

    def __init__(self, servers):
        self.client = None
        self.channels = set()
        self.setServers(servers)

    def setServers(self, servers):
        random.shuffle(servers)
        self.servers = servers
        self.n_server = 0

    def reconnect(self):
        server = self.servers[self.n_server]
        self.n_server = (self.n_server + 1) % len(self.servers)
        a = server.split(":")
        if len(a) == 1:
            ip, port = a[0], 1883
        else:
            ip, port = a[0], int(a[1])
        self.client = mosquitto.Mosquitto('swarming')
        self.client.on_connect = self.on_connect
        #self.client.reconnect_delay_set(10, 3600, True)
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        print "try to connect to", ip, port
        self.client.connect(ip, port=port)

    def lazy_loop(self):
        if self.client is None or self.client._sock is None:
            self.reconnect()
        self.client.loop()

    def subscribe(self, path):
        self.channels.add(path)

    def publish(self, topic, payload=None, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def on_disconnect(self, mosq, obj, rc):
        print "disconnect", mosq

    def on_connect(self, mosq, obj, rc):
        print "connect", self.client._host, self.client._port, rc
        if rc == 0:
            self.state = 'connected'
            for channel in self.channels:
                mosq.subscribe(channel)

    def on_message(self, mosq, obj, msg):
        print msg.topic
        print msg.payload
        if msg.topic == "watch":
            print "change watch"
            targets = msg.payload.split(' ')
            random.shuffle(targets)
            self.ping.targets = targets
        # FIXME python3 hates string type mismatch
        #print("Message received on topic "+msg.topic+" with id "+str(msg.mid)+
        #" with QoS "+str(msg.qos)+" and payload "+msg.payload)

    def loop(self):
        self.ping = Ping('free.fr', 'yahoo.fr', 'voila.fr', 'www.doctissimo.fr')
        while True:
            try:
                self.lazy_loop()
                self.ping.lazy_start()
                r = self.ping.poll()
                if r is not None:
                    success, target, message = r
                    self.publish('ping/%s' % target, json.dumps(
                        {success: message}))
                print ".",
            except socket.error as e:
                print "oups", e


if len(sys.argv) == 1:
    m = MetaClient(["localhost", "127.0.0.1:1884"])
else:
    m = MetaClient(sys.argv[1:])
m.subscribe('watch')
m.loop()

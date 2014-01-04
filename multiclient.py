import socket

import paho.mqtt.client as paho


class MultiClient(object):

    def __init__(self, servers, channels, prefix=""):
        self.servers = []
        self.channels = channels
        for server in servers:
            client = paho.Client(client_id="sw/%s/%s" %
                                 (prefix, socket.gethostname()),
                                 clean_session=False)
            client.on_connect = self.on_connect
            client.on_disconnect = self.on_disconnect
            client.on_message = self.on_message
            self.servers.append(client)
            client.connect_async(server)

    def on_connect(self, client, userdata, rc):
        if rc == 0:
            for channel in self.channels:
                client.subscribe(channel, qos=2)
        else:
            raise Exception('Connection error %i' % rc)

    def on_disconnect(self, client, userdata, rc):
        print "diconnected", rc

    def on_message(self, client, userdata, message):
        if message is None:
            return
        print message.timestamp
        print message.qos, message.mid
        print message.topic
        print message.payload

    def loop(self):
        for client in self.servers:
            try:
                if client._sock is None:
                    client.reconnect()
                else:
                    client.loop()
            except socket.error as e:
                print "oups", e

import paho.mqtt.client as paho


class MultiClient(object):

    def __init__(self, servers, channels):
        self.servers = []
        self.channels = channels
        for server in servers:
            client = paho.Client(None, True)
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.connect(server)
            self.servers.append(client)

    def on_connect(self, client, userdata, rc):
        if rc == 0:
            for channel in self.channels:
                client.subscribe(channel, qos=2)
        else:
            raise Exception('Connection error %i' % rc)

    def on_message(self, client, userdata, message):
        if message is None:
            return
        print message.timestamp
        print message.qos, message.mid
        print message.topic
        print message.payload

    def loop(self):
        for server in self.servers:
            server.loop()

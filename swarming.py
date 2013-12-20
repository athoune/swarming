import mosquitto


class MetaClient(object):

    def __init__(self, servers):
        self.clients = []
        for server in servers:
            a = server.split(":")
            if len(a) == 1:
                ip, port = a[0], 1883
            else:
                ip, port = a[0], int(a[1])
            m = mosquitto.Mosquitto('swarming')
            m.connect(ip, port=port)
            m.on_message = on_message
            self.clients.append(m)

    def subscribe(self, path):
        for client in self.clients:
            client.subscribe(path)

    def loop(self):
        while True:
            for client in self.clients:
                client.loop()


def on_message(mosq, obj, msg):
    print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)

m = MetaClient(["localhost", "127.0.0.1:1884"])
m.subscribe('watch')
m.loop()

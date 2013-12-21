import mosquitto


class MetaClient(object):

    def __init__(self, servers):
        self.clients = []
        self.channels = set()
        for server in servers:
            a = server.split(":")
            if len(a) == 1:
                ip, port = a[0], 1883
            else:
                ip, port = a[0], int(a[1])
            m = mosquitto.Mosquitto('swarming')
            m.on_connect = self.on_connect
            m.reconnect_delay_set(30, 3600, True)
            m.on_message = self.on_message
            m.on_disconnect = self.on_disconnect
            self.clients.append(m)
            m.connect_async(ip, port=port)

    def subscribe(self, path):
        self.channels.add(path)

    def publish(self, topic, payload=None, qos=0, retain=False):
        for client in self.clients:
            client.publish(topic, payload, qos, retain)

    def on_disconnect(self, mosq, obj, rc):
        pass

    def on_connect(self, mosq, obj, rc):
        if rc == 0:
            for channel in self.channels:
                mosq.subscribe(channel)

    def on_message(self, mosq, obj, msg):
        print("Message received on topic "+msg.topic+" with id "+str(msg.mid)+" with QoS "+str(msg.qos)+" and payload "+msg.payload)

    def loop(self):
        while True:
            for client in self.clients:
                if client._sock == None:
                    try:
                        client.reconnect()
                    except socket.error:
                        print "*"
                client.loop(1)
            print ".",


m = MetaClient(["localhost", "127.0.0.1:1884"])
m.subscribe('watch')
m.loop()

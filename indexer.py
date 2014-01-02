import json

from multiclient import MultiClient


class Indexer(MultiClient):
    def on_message(self, client, userdata, message):
        if message is None:
            return
        data = json.loads(message.payload)
        topics = message.topic.split('/')
        if topics[0] == u'ping':
            agent, success, values = data
            min_, avg, max_, stddev = values[u'Round trip']
            loss = values[u'loss']
            print agent, topics[1], avg, loss


if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) == 1:
        os.exit()
    client = Indexer(sys.argv[1:], ['ping/+'])
    while True:
        client.loop()
        print '.',

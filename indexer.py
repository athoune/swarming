import json

from multiclient import MultiClient
from elasticsearch import Elasticsearch


class Indexer(MultiClient):

    def __init__(self, servers, channels, elasticsearch):
        super(Indexer, self).__init__(servers, channels)
        self.es = elasticsearch

    def on_message(self, client, userdata, message):
        if message is None:
            return
        data = json.loads(message.payload)
        topics = message.topic.split('/')
        if topics[0] == u'ping':
            agent, success, values = data
            min_, avg, max_, stddev = values[u'Round trip']
            loss = values[u'loss']
            print agent, topics[1], avg, loss, message.timestamp


if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) == 1:
        os.exit()
    es = Elasticsearch()
    client = Indexer(sys.argv[1:], ['ping/+'], es)
    while True:
        client.loop()
        print '.',

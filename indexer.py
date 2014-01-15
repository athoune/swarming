import json
from datetime import datetime

from multiclient import MultiClient
from elasticsearch import Elasticsearch


class Indexer(MultiClient):

    def __init__(self, servers, channels, elasticsearch):
        super(Indexer, self).__init__(servers, channels, prefix="indexer")
        self.es = elasticsearch
        self.last_index = None

    def on_message(self, client, userdata, message):
        if message is None:
            return
        if message.payload is not None and len(message.payload) > 0:
            data = json.loads(message.payload)
        else:
            data = None
        topics = message.topic.split('/')
        if topics[0] == u'ping':
            self.on_ping(topics, data, message.timestamp)
        elif topics[0] == u'rip':
            self.on_rip(topics, message.timestamp)
        else:
            print(u"Strange topics : %s" % topics)

    def lazy_index(self, dt):
        idx = dt.date().strftime('logstash-%Y.%m.%d')
        if idx != self.last_index and not self.es.indices.exists(idx):
            self.last_index = idx
            self.es.indices.create(idx, body={
                'mappings': {
                    'ping': {
                        'properties': {
                            '@timestamp': {
                                'type': 'date'
                            }
                        }
                    },
                    'rip': {
                        'properties': {
                            '@timestamp': {
                                'type': 'date'
                            }
                        }
                    }
                }
            })
        return idx

    def on_rip(self, topics, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        idx = self.lazy_index(dt)
        agent = topics[2]  # Assuming just agent is dying
        print(self.es.index(index=idx, doc_type='rip', body={
            '@timestamp': dt.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
            '@version': 1,
            'message': "",
            'agent': agent
        }))

    def on_ping(self, topics, data, timestamp):
        agent, success, values = data
        if success != 'ok':
            return
        dt = datetime.fromtimestamp(timestamp)
        idx = self.lazy_index(dt)
        if values['loss'] == 100.0:
            min_, avg, max_, stddev = [None, None, None, None]
        else:
            min_, avg, max_, stddev = values[u'Round trip']
        loss = values[u'loss']
        print(self.es.index(index=idx, doc_type='ping', body={
            '@timestamp': dt.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
            '@version': 1,
            'message': "",
            'agent': agent,
            'target': topics[1],
            'avg': avg,
            'min': min_,
            'max': max_,
            'stddev': stddev,
            'loss': loss
        }
        ))


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        sys.exit()
    es = Elasticsearch()
    client = Indexer(sys.argv[1:], ['ping/+', 'rip/#'], es)
    while True:
        client.loop()
        print '.',

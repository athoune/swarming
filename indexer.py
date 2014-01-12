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
        data = json.loads(message.payload)
        topics = message.topic.split('/')
        if topics[0] == u'ping':
            agent, success, values = data
            if success != 'ok':
                return
            min_, avg, max_, stddev = values[u'Round trip']
            loss = values[u'loss']
            dt = datetime.fromtimestamp(message.timestamp)
            idx = dt.date().strftime('logstash-%Y.%m.%d')
            if idx != self.last_index and not self.es.indices.exists(idx):
                self.last_index = idx
                self.es.indices.create(idx, body={
                    'mappings':{
                        'ping': {
                            'properties': {
                                '@timestamp': {
                                    'type': 'date'
                                }
                            }
                        }
                    }
                })
            print self.es.index(index=idx, doc_type='ping', body={
                '@timestamp':dt.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
                '@version':1,
                'message': "",
                'agent':agent,
                'target':topics[1],
                'avg': avg,
                'min':min_,
                'max':max_,
                'stddev':stddev,
                'loss':loss
            }
            )


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        sys.exit()
    es = Elasticsearch()
    client = Indexer(sys.argv[1:], ['ping/+'], es)
    while True:
        client.loop()
        print '.',

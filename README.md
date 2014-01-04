Swarming
========

Handling a swarm of pingers.

Pingers are, using different ISP, different technology, in different places.
Pingers wait for targets, and ping them, periodicaly.

It's the DDOS pattern for quietly testing connection quality, and answering the
remote worker question : it's just me, or this service is slow?

For now, only classical ping is used (the ICMP one), later, http ping will be handled.

Architecture
------------

All communiction is done via MQTT, with more than one broker.
Network cut is expected.

_Agents_ listen a chan for a list of targets.
Agents sequentialy ping targets, send results and wait before its netx move.
Agent action are not coordinated, random is used as a poor man dispatcher.
Agent use harcoded wait time and cannot be used to DOS anything larger than an Arduino ethernet.
Agent should store message that it can't send, it continues is duty, even without online broker.
Agent should use TLS certificate authentication.

The _indexer_, another mqtt client, listen for results, and index messages.

### Agents

Connection technology should be representative,
with ADSL, cable, fiber, GPRS, Edge, 3G and even 4G.

Different location can be used to test CDN and world wide latencies.

Agent uses python 2.7, with just one pure python dependency : mosquitto client library.
Pypy works nice too, but it's just coincidence.
Python 3 needs more loves.

### Broker

The broker is just a Mosquitto server. Any MQTT 3.1 server should work.

### Indexer

The indexer index messages for Kibana drills.
![Kibana screenshot](https://raw.github.com/athoune/swarming/master/kibana.png "Kibana screenshot")

Trying it
---------

Prepare the python stuffs:

    virtualenv .
    ./bin/pip install -r requirements.txt

Launch some mqtt server:

    mosquitto

Launch one listener:

    mosquitto_sub -t "ping/+" -v

Launch the agent:

    ./bin/python swarming.py localhost

Wait a bit and change the list of targets:

    mosquitto_pub -t watch -m "voila.fr yahoo.cn prout.local palourde.net" -q 1

State of the project
--------------------

Fighting with callback, polling and select, the old way.

python-mosquitto package on Debian is old and use ctype binding.
Current lib is pure python. Paho project is eating Mosquitto.

Python's hard synchronicity is weird when you already put a foot in the land of asynchronicity.

 * √ Use multiple brokers
 * √ Reconnect when a broker is back
 * √ Subprocess for ping
 * √ Publish a result to its own chan
 * √ Listen for targets, and use them
 * √ Index messages
 * _ Guess connection type
 * _ Httping

# The Python script to forward messages from MQTT to Statsd server

The script for forwarding messages works in several threads, depending on the number of listened to topics.
The message type for the Statsd server is always gauge

When receiving a message from MQTT topic the script parses the topic into components and converts path separators from / to . then sends it to the Statsd server along the generated path

## Install and config
- Download the required repository;

```bash
$ git clone https://github.com/leech001/mqtt2statsd.git
```

- Change dir to mqtt2statsd/mqtt2statsd/application/ and edit config.yaml file;

```yaml
statsd:
  hostname: statsd.server.ru  # Statsd server hostname
  port: 8125                  # Statsd server port
  prefix: mqtt                # Statsd prefix for metrics
mqtt:
  hostname: mqtt.server.ru    # MQTT server hostname
  port: 1883                  # MQTT server port
  keepalive: 60               # MQTT keepalive
  username: user              # MQTT auth user
  password: pass              # MQTT auth pass
topics:
  - mqtt_topic: homeassistant/home/#    #Example topic
```

## Run
- Change dir to /mqtt2statsd and run docker container;
```bash
    $ sudo docker-compose up -d
```

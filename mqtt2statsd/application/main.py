import sys
import threading
import signal
import paho.mqtt.client as mqtt
import statsd
import yaml


class MQTTStat(threading.Thread):

    def __init__(self, statsd_client, hostname, topic, port=1883, keepalive=60, auth=None):
        super(MQTTStat, self).__init__()
        self.hostname = hostname
        self.port = port
        self.keepalive = keepalive
        self.mqtt_topic = topic
        self.auth = auth
        self.statsd_client = statsd_client
        self.client = mqtt.Client()
        if auth:
            self.client.username_pw_set(auth['username'], password=auth.get('password'))

    def run(self):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.mqtt_topic)

        def on_message(client, userdata, msg):
            try:
                payload = float(msg.payload)
                self.statsd_client.gauge(msg.topic.replace('/', '.'), payload)
            except Exception:
                pass

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(self.hostname, self.port, keepalive=self.keepalive)
        self.client.loop_forever()


def main():
    with open("config.yaml", 'r') as conf:
        config = yaml.safe_load(conf)

    # Read statsd config
    if 'statsd' not in config:
        print('No statsd section found in specified config file')
        sys.exit(2)

    statsd_host = config['statsd'].get('hostname')
    if not statsd_host:
        print('No valid statsd hostname provided in config file')
        sys.exit(2)
    statsd_port = config['statsd'].get('port', 8125)
    if not statsd_port:
        print('No valid statsd port provided in config file')
    statsd_prefix = config['statsd'].get('prefix', 'mosquitto.stats')
    statsd_client = statsd.StatsClient(host=statsd_host, port=statsd_port, prefix=statsd_prefix)

    # Read MQTT config
    if 'mqtt' not in config:
        print('No MQTT section found in the specified config file')
        sys.exit(2)
    mqtt_hostname = config['mqtt'].get('hostname')
    if not mqtt_hostname:
        print('No valid mqtt hostname provided in the config file')
        sys.exit(2)
    mqtt_port = config['mqtt'].get('port', 1883)
    mqtt_keepalive = config['mqtt'].get('keepalive', 60)
    # Configure MQTT auth
    auth = None
    username = config['mqtt'].get('username')
    if username:
        auth = {'username': username}
    password = config['mqtt'].get('password')
    if password and auth:
        auth['password'] = password

    # Listen to topics and start statsd reporters
    if 'topics' not in config:
        print('No topics specified in the config file')
        sys.exit(2)

    for topic in config['topics']:
        mqtt_topic = topic.get('mqtt_topic')
        if not mqtt_topic:
            print("No mqtt_topic specified for an entry in topics list")
            sys.exit(3)
        thread = MQTTStat(statsd_client, mqtt_hostname, mqtt_topic, mqtt_port, auth=auth, keepalive=mqtt_keepalive)
        thread.start()

    while True:
        signal.pause()


if __name__ == '__main__':
    main()

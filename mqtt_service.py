import machine
import time
import json
from umqtt.simple import MQTTClient

class MQTTService:
    """
    publish_messages() takes any number of arguments. They should all be
    iterable and return tuple containing topic (to publish) and payload pair.
    The payload can be a dict or be a type than can be converted to a
    string using str()
    """
    def __init__(self, cfg_set, mqtt_set, sub_cb = False):
        self.last_msg      = 0
        self.start_time    = time.time()
        self.mqtt_set      = mqtt_set
        self.sub_cb        = sub_cb
        try:
            self.client = MQTTClient(self.mqtt_set['client_id'],
                                     cfg_set['broker_addr'],
                                     user = cfg_set['broker_usrname'],
                                     password = cfg_set['broker_psswrd'])
            self.client.connect()
            if self.sub_cb:
                self.client.set_callback(self.sub_cb)
                self.client.subscribe('{0}/{1}'.format(self.mqtt_set['base_topic'],
                                                       self.mqtt_set['topic_sub']))
            self.publish_settings()
        except:
            self._restart_and_connect()

    def publish_messages(self, *messages):
        self.publish_settings()
        for message in messages:
            if hasattr(message, '__iter__'):
                for topic, payload in message:
                    topic_pub = '{0}/{1}'.format(self.mqtt_set['base_topic'], topic)
                    if isinstance(payload, dict):
                        self._publish(topic_pub, json.dumps(payload))
                    else:
                        self._publish(topic_pub, str(payload))
            elif isinstance(message, (tuple,list)):
                topic, payload = message
                topic_pub = '{0}/{1}'.format(self.mqtt_set['base_topic'], topic)
                if isinstance(payload, dict):
                    self._publish(topic_pub, json.dumps(payload))
                else:
                    self._publish(topic_pub, str(payload))

    def publish_settings(self):
        tm = time.localtime()
        self.mqtt_set['pub_time'] = (
            '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(tm[0], tm[1],
            tm[2], tm[3] + 1, tm[4], tm[5]))
        topic_pub = '{0}/{1}'.format(self.mqtt_set['base_topic'],
                                     self.mqtt_set['topic_set'])
        self._publish(topic_pub, json.dumps(self.mqtt_set))

    def _publish(self, topic, payload):
        try:
            self.client.publish(topic, payload)
        except:
            self._restart_and_connect()

    def _restart_and_connect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()

    def loop(self):
        self.client.check_msg()

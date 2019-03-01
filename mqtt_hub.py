import machine
import time
import json
from umqtt.simple import MQTTClient

class MQTThub:
    """
    nodes qualifying for addition via add_node() should return key (topic) and
    value (message) pair in an iterable fashion
    any number of nodes can be added
    """
    def __init__(self, mqtt_set, sub_cb = False):
        self.last_msg      = 0
        self.start_time    = time.time()
        self.mqtt_set      = mqtt_set
        self.nodes         = []
        self.sub_cb        = sub_cb
        try:
            self.client = MQTTClient(self.mqtt_set['client_id'],
                                     self.mqtt_set['broker_addr'],
                                     user = self.mqtt_set['broker_usrname'],
                                     password = self.mqtt_set['broker_psswrd'])
            self.client.connect()
            if self.sub_cb:
                self.client.set_callback(self.sub_cb)
                self.client.subscribe('{0}/{1}'.format(self.mqtt_set['base_topic'],
                                                       self.mqtt_set['topic_sub']))
            self.publish_settings()
        except OSError as e:
            self._restart_and_connect()

    def add_node(self, node):
        self.nodes.append(node)

    def publish_nodes(self):
        self.publish_settings()
        for node in self.nodes:
            for key, value in node:
                topic_pub = '{0}/{1}'.format(self.mqtt_set['base_topic'], key)
                if isinstance(value, dict):
                    self.client.publish(topic_pub, json.dumps(value))
                else:
                    self.client.publish(topic_pub, str(value))

    def publish_settings(self):
        tmp_dict = {}
        tmp_dict['client_id']    = self.mqtt_set['client_id']
        tmp_dict['msg_interval'] = self.mqtt_set['msg_interval']
        tmp_dict['uptime']       =  time.time()-self.start_time
        topic_pub = '{0}/{1}'.format(self.mqtt_set['base_topic'],
                                     self.mqtt_set['topic_set'])
        self.client.publish(topic_pub, json.dumps(tmp_dict))

    def _restart_and_connect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()

    def loop(self):
        try:
            self.client.check_msg()
            duration = time.time() - self.last_msg
            if self.nodes and (duration > self.mqtt_set['msg_interval']):
                self.publish_nodes()
                self.last_msg = time.time()
        except OSError as e:
            self._restart_and_connect()

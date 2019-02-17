from ubinascii import hexlify
import machine
import json

from mqtt_hub import MQTThub
from sensor_factory import SensorFactory
from switch_factory import SwitchFactory

mqtt_settings = {
    'broker_addr'   : '192.168.0.200',
    'broker_usrname': 'henrik',
    'broker_psswrd' : 'ag1pno3m',
    'client_id'     : hexlify(machine.unique_id()),
    'base_topic'    : 'home/kitchen/ESP32_01',
    'topic_set'     : 'settings',   # topic to which settings are published
    'topic_sub'     : 'adjust',     # subscribed topic
    'msg_interval'  : 60 }          # publishing frequency - can be updated
                                    # by sending {'msg_interval':0} to tupic
                                    # base_topic/topic_sub

switch_settings = {
    'display' : {'clk_pin' : 2, 'dio_pin' : 0, 'brightness' : 5}
}

# function receiving messages from subscribed topic (base_topic/topic_sub)
def sub_cb(topic, msg):
    try:
        msg_dict = json.loads(msg)
        print('incoming msg received:', msg)
        if 'msg_interval' in msg_dict:
            mqtt_settings['msg_interval'] = int(msg_dict['msg_interval'])
    except:
        print('error converting incoming msg:', msg)
    mqtt_hub.publish_settings()

# instantiation of SensorFactory
sf = SensorFactory(i2c)

# instantiation of MQTThub and addition of nodes via iterable sf object
mqtt_hub = MQTThub(mqtt_settings, sub_cb)
mqtt_hub.add_node(sf)

# loop can be terminated by sending {'msg_interval':0} message to
# topic based_topic/topic_sub (see mqtt_settings above)
#while mqtt_settings['msg_interval'] != 0:
#    mqtt_hub.loop()

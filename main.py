from ubinascii import hexlify
import machine
import json
from mqtt_hub import MQTThub
from sensor_factory import SensorFactory

import schedule
from tm1637_display import TM1637Display

mqtt_settings = {
    'broker_addr'   : '',
    'broker_usrname': '',
    'broker_psswrd' : '',
    'client_id'     : hexlify(machine.unique_id()),
    'base_topic'    : 'home/kitchen/ESP32_01',
    'topic_set'     : 'settings',   # topic to which settings are published
    'topic_sub'     : 'adjust',     # subscribed topic
    'msg_interval'  : 60 }          # publishing frequency - can be updated
                                    # by sending {'msg_interval':0} to tupic
                                    # base_topic/topic_sub

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

tmdisp = TM1637Display()


schedule.every(6).seconds.do(tmdisp.show, output = sf.humidity)
schedule.every(4).seconds.do(tmdisp.show, output = sf.co2eq)

# loop can be terminated by sending {'msg_interval':0} message to
# topic based_topic/topic_sub (see mqtt_settings above)
while True:
    mqtt_hub.loop()
    schedule.run_pending()

from ubinascii import hexlify
import machine
import json
from mqtt_service import MQTTService
from sensor_factory import SensorFactory
import nodes

import schedule
from tm1637_display import TM1637Display

mqtt_settings = {
    'client_id'     : hexlify(machine.unique_id()),
    'base_topic'    : 'home/kitchen/ESP32_01',
    'topic_set'     : 'settings',   # topic to which settings are published
    'topic_sub'     : 'adjust',     # subscribed topic
    'start_time'    : start_time }


# function receiving messages from subscribed topic (base_topic/topic_sub)
def sub_cb(topic, msg):
    try:
        msg_dict = json.loads(msg)
        print('incoming msg received:', msg)
        if 'msg_interval' in msg_dict:
            mqtt_settings['msg_interval'] = int(msg_dict['msg_interval'])
    except:
        print('error converting incoming msg:', msg)
    mqtt.publish_settings()

# instantiation of SensorFactory
sf = SensorFactory(i2c)

# instantiation of MQTThub and addition of nodes via iterable sf object
mqtt = MQTTService(config['mqtt'], mqtt_settings, sub_cb)

tmdisp = TM1637Display()


schedule.every(6).seconds.do(tmdisp.show, output = sf.humidity)
schedule.every(4).seconds.do(tmdisp.show, output = sf.co2eq)


#while True:
#    mqtt.loop()
#    schedule.run_pending()

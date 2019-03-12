import machine
import json
from ubinascii import hexlify
from sensors import HTU21D_i2c, SGP30_i2c, BMP180_i2c, TSL2561_i2c
from nodes import Nodes
from mqtt_service import MQTTService
from scheduler import Schedule

#import schedule
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

# instantiation of Nodes
nodes = Nodes()
nodes.add(HTU21D_i2c(i2c)).add(BMP180_i2c(i2c))
nodes.add(SGP30_i2c(i2c)).add(TSL2561_i2c(i2c))

# instantiation of MQTThub and addition of nodes via iterable sf object
mqtt = MQTTService(config['mqtt'], mqtt_settings, sub_cb)

tmdisp = TM1637Display()

#while True:
#    mqtt.loop()
#    schedule.run_pending()

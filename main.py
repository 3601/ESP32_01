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
    'topic_set'     : 'settings/out',   # topic to which settings are published
    'topic_sub'     : 'settings/in/#',     # subscribed topic
    'start_time'    : start_time }

# function receiving messages from subscribed topic (base_topic/topic_sub)
def sub_cb(topic, msg):
    """ rember to account for active argument -> toggle on/off"""
    if 'display' in topic:
        try:
            msg_dict = json.loads(msg)
        except:
            tmdisp.show(' err')
            mqtt.publish_messages(schedule, ext = mqtt_settings['topic_set'] +
                                                                '/schedule')
            return
        interval  = msg_dict.get('interval', None)
        unit      = msg_dict.get('unit', None)
        start_day = msg_dict.get('start_day', None)
        at_time   = msg_dict.get('at_time', None)
        if 'property' in msg_dict and msg_dict['property'] in nodes:
            if (interval, unit, start_day, at_time).count(None) < 4:
                if schedule.every(tag = 'display', interval = interval,
                                  unit = unit, start_day = start_day,
                                  at_time = at_time):
                    tmdisp.add_display_func(nodes[msg_dict['property']])
                    tmdisp.show('pend')
                else:
                    tmdisp.show(' err')
            else:
                tmdisp.add_display_func(nodes[msg_dict['property']])
                tmdisp.show('pend')
        mqtt.publish_messages(schedule, ext = mqtt_settings['topic_set'] +
                                                            '/schedule')
    elif 'sensors' in topic:
        try:
            msg_dict = json.loads(msg)
        except:
            mqtt.publish_messages(schedule, ext = mqtt_settings['topic_set'] +
                                                                '/schedule')
            return
        interval  = msg_dict.get('interval', None)
        unit      = msg_dict.get('unit', None)
        start_day = msg_dict.get('start_day', None)
        at_time   = msg_dict.get('at_time', None)
        if (interval, unit, start_day, at_time).count(None) < 4:
            schedule.every(tag = 'sensors', interval = interval,
                           unit = unit, start_day = start_day,
                           at_time = at_time)
        mqtt.publish_messages(schedule, ext = mqtt_settings['topic_set'] +
                                                            '/schedule')


# instantiation of Nodes
nodes = Nodes()
nodes.add(HTU21D_i2c(i2c)).add(BMP180_i2c(i2c))
nodes.add(SGP30_i2c(i2c)).add(TSL2561_i2c(i2c))

# instantiation of MQTThub and addition of nodes via iterable sf object
mqtt = MQTTService(config['mqtt'], mqtt_settings, sub_cb)

# instantiation of TM1637 display class
tmdisp = TM1637Display()
tmdisp.add_display_func(nodes.co2eq)

# instantiation of Schedule class
schedule = Schedule()
schedule.every(tag = 'display', interval = 5, unit = 'sec', job_func = tmdisp.show)
schedule.every(tag = 'sensors', interval = 10, unit = 'sec',
               job_func = mqtt.publish_messages, msg = nodes)

# continuously check for incoming messages and scheduled jobs
while True:
    mqtt.loop()
    schedule.run_pending()

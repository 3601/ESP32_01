# load configuration on the microprocessor
import json
with open('config.json', 'r') as f:
    config = json.loads(f.read())

# functions to establish Wifi connection
def no_debug():
    import esp
    esp.osdebug(None)

def connect(ssid, password):
    import network
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        print('connecting to network...')
        station.active(True)
        station.connect(ssid, password)
        while not station.isconnected():
            pass
    print('network config:', station.ifconfig())

# connect to Wifi
no_debug()
connect(config['wifi']['ssid'], config['wifi']['psswrd'])

# synchronize board time using NTP (UTC) and store current time in string
from ntptime import settime
import time
settime()
tm = time.localtime()
start_time = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(tm[0], tm[1],
    tm[2], tm[3] + 1, tm[4], tm[5])

# establish I2C connection
from machine import Pin, I2C
i2c = I2C(sda = Pin(21), scl = Pin(22))
# print('I2C devices on:', ', '.join([hex(i) for i in i2c.scan()]))

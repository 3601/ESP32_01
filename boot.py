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
import utils
settime()
#tm = time.localtime()
tm = utils.cettime()
start_time = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(*tm[:6])

# establish I2C connection
from machine import Pin, I2C
i2c = I2C(sda = Pin(21), scl = Pin(22))
# print('I2C devices on:', ', '.join([hex(i) for i in i2c.scan()]))

def connected_i2c_devices(i2c):
    # print connected i2c devices
    i2c_addr = { '0x40' : 'HTU21D (0x40)',
                 '0x58' : 'SGP30 (0x58)',
                 '0x77' : 'BMP180 (0x77)',
                 '0x39' : 'TSL2561 (0x39)' }

    print('I2C devices: ', end = '')
    for dev in i2c.scan():
        try:
            print(i2c_addr[hex(dev)], end = ', ')
        except:
            print('unknown ({0})'.format(hex(dev)), end = ', ')
    print()

connected_i2c_devices(i2c)

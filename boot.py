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
connect('CableBox-2715', 'udm2qgmhtn')

# establish I2C connection
from machine import Pin, I2C
i2c = I2C(sda = Pin(21), scl = Pin(22))
# print('I2C devices on:', ', '.join([hex(i) for i in i2c.scan()]))

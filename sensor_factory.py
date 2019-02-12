from htu21d import HTU21D
from adafruit_sgp30 import Adafruit_SGP30
from bmp180 import BMP180
from tsl2561 import TSL2561

class SensorFactory:
    """
    nodes can be accessed
    1) in iterable fashion: 'sensor_name, sensor_value in SensorFactory'
    2) using in index: 'SensorFactory[sensor_name]'
    3) by calling relevant function 'SensorFactory.sensor_name()'
    """

    def temperature(self):
        tmp_dict = {}
        temp_tmp = self.htu21d.temperature()
        if temp_tmp != None:
            tmp_dict['value'] = round(temp_tmp, 2)
        else:
            tmp_dict['value'] = 'error'
        tmp_dict['unit'] = 'celcius'
        tmp_dict['sensor'] = 'HTU21D'
        return tmp_dict

    def humidity(self):
        tmp_dict = {}
        humid_tmp = self.htu21d.humidity()
        if humid_tmp != None:
            tmp_dict['value'] = round(humid_tmp, 2)
        else:
            tmp_dic['value'] = 'error'
        tmp_dict['unit'] = 'percent'
        tmp_dict['sensor'] = 'HTU21D'
        return tmp_dict

    def co2eq(self):
        tmp_dict = {}
        tmp_dict['value'] = self.sgp30.co2eq
        tmp_dict['unit']  = 'ppm'
        tmp_dict['sensor'] = 'SGP30'
        tmp_dict['baseline'] = self.sgp30.baseline_co2eq
        return tmp_dict

    def tvoc(self):
        tmp_dict = {}
        tmp_dict['value'] = self.sgp30.tvoc
        tmp_dict['unit']  = 'ppm'
        tmp_dict['sensor'] = 'SGP30'
        tmp_dict['baseline'] = self.sgp30.baseline_tvoc
        return tmp_dict

    def pressure(self):
        tmp_dict = {}
        tmp_dict['value'] = round(self.bmp180.pressure / 1000, 3)
        tmp_dict['unit']  = 'kPa'
        tmp_dict['sensor'] = 'BMP180'
        tmp_dict['temperature'] = round(self.bmp180.temperature, 2)
        return tmp_dict

    def luminosity(self):
        tmp_dict = {}
        tmp_dict['value'] = round(self.tsl2561.read(autogain = True), 3)
        tmp_dict['unit']  = 'LUX'
        tmp_dict['sensor'] = 'TSL2561'
        return tmp_dict

    def __init__(self, i2c):

        self.i2c = i2c

        # print connected i2c devices
        self.sensor_addr = { '0x40' : 'HTU21D (0x40)',
                             '0x58' : 'SGP30 (0x58)',
                             '0x77' : 'BMP180 (0x77)',
                             '0x39' : 'TSL2561 (0x39)' }

        print('I2C devices: ', end = '')
        for dev in self.i2c.scan():
            try:
                print(self.sensor_addr[hex(dev)], end = ', ')
            except:
                print('unknown ({0})'.format(hex(dev)), end = ', ')
        print()

        # instantiate HTU21D sensor
        self.htu21d = HTU21D(self.i2c)

        # instantiate SGP30 sensor
        self.sgp30 = Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        #self.sgp30.set_iaq_baseline(0x8973, 0x8aae)

        # instantiate BMP180 sensor
        self.bmp180 = BMP180(i2c)

        # instantiate TSL2561 sensor
        self.tsl2561 = TSL2561(i2c)
        self.tsl2561.gain(16)
        self.tsl2561.integration_time(13)

        # dictionary with key = property, value = function
        self.sensors = {}
        self.sensors['temperature'] = self.temperature
        self.sensors['humidity']    = self.humidity
        self.sensors['co2eq']       = self.co2eq
        self.sensors['tvoc']        = self.tvoc
        self.sensors['pressure']    = self.pressure
        self.sensors['luminosity']  = self.luminosity

    def __iter__(self):
        self.sensors_keys = list(self.sensors.keys())
        return self

    def __next__(self):
        if len(self.sensors_keys) >= 1:
            tmp_key = self.sensors_keys.pop()
            return tmp_key, self.sensors[tmp_key]()
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.sensors[key]()

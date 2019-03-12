
from htu21d import HTU21D
from adafruit_sgp30 import Adafruit_SGP30
from bmp180 import BMP180
from tsl2561 import TSL2561

class Sensor:
    def __init__(self, i2c):
        self.i2c = i2c
        pass

class SGP30_i2c(Sensor):
    @property
    def connected(self):
        # '0x58' : 'SGP30 (0x58)'
        return int(0x58) in self.i2c.scan()

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

    def __init__(self, i2c):
        self.i2c = i2c
        self.sgp30 = Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        self.info = {'sensor'  : 'SGP30',
                     'readout' : {'co2eq' : self.co2eq, 'tvoc' : self.tvoc}}

class HTU21D_i2c(Sensor):
    @property
    def connected(self):
        # '0x40' : 'HTU21D (0x40)'
        return int(0x40) in self.i2c.scan()

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

    def __init__(self, i2c):
        self.i2c = i2c
        self.htu21d = HTU21D(self.i2c)
        self.info = {'sensor'  : 'HTU21D',
                     'readout' : {'temperature' : self.temperature,
                                   'humidity' : self.humidity}}

class BMP180_i2c(Sensor):
    @property
    def connected(self):
        # '0x77' : 'BMP180 (0x77)'
        return int(0x77) in self.i2c.scan()

    def pressure(self):
        tmp_dict = {}
        tmp_dict['value'] = round(self.bmp180.pressure / 1000, 3)
        tmp_dict['unit']  = 'kPa'
        tmp_dict['sensor'] = 'BMP180'
        tmp_dict['temperature'] = round(self.bmp180.temperature, 2)
        return tmp_dict

    def __init__(self, i2c):
        self.i2c = i2c
        self.bmp180 = BMP180(self.i2c)
        self.info = {'sensor'  : 'BMP180',
                     'readout' : {'pressure' : self.pressure}}

class TSL2561_i2c(Sensor):
    @property
    def connected(self):
        # '0x39' : 'TSL2561 (0x39)'
        return int(0x39) in self.i2c.scan()

    def luminosity(self):
        tmp_dict = {}
        tmp_dict['value'] = round(self.tsl2561.read(self.set_autogain), 3)
        tmp_dict['unit']  = 'lux'
        tmp_dict['sensor'] = 'TSL2561'
        return tmp_dict

    def __init__(self, i2c, set_autogain = True, set_gain = 16,
                 set_int_time = 13):
        self.i2c = i2c
        self.set_autogain = set_autogain
        self.tsl2561 = TSL2561(self.i2c)
        self.tsl2561.gain(set_gain)
        self.tsl2561.integration_time(set_int_time)
        self.info = {'sensor'  : 'TSL2561',
                     'readout' : {'luminosity' : self.luminosity}}

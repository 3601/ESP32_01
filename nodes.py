from sensors import HTU21D_i2c, SGP30_i2c, BMP180_i2c, TSL2561_i2c

class Nodes:
    """
    nodes can be accessed
    1) in iterable fashion: 'sensor_name, sensor_value in SensorFactory'
    2) using in index: 'SensorFactory[sensor_name]'
    3) by calling relevant function 'SensorFactory.sensor_name()'
    """

    def detect_nodes(self):
        print('I2C devices: ')
        for key in self.nodes['sensors']:
            print('{0:<8} connected: {1}'.format(self.nodes['sensors'][key].connected()))

    def __init__(self, i2c, verbose = True):
        self.i2c = i2c

        self.nodes = {}
        self.nodes['sensors']['HTU21D']  = HTU21D_i2c(self.i2c)
        self.nodes['sensors']['SGP30']   = SGP30_i2c(self.i2c)
        self.nodes['sensors']['BMP180']  = BMP180_i2c(self.i2c)
        self.nodes['sensors']['TSL2561'] = TSL2561_i2c(self.i2c)

        self.nodes['sensor']['temperature'] = self.nodes['sensors']['HTU21D'].temperature
        self.nodes['sensor']['humidity']    = self.nodes['sensors']['HTU21D'].humidity
        self.nodes['sensor']['co2eq']       = self.nodes['sensors']['SGP30'].co2eq
        self.nodes['sensor']['tvoc']        = self.nodes['sensors']['SGP30'].tvoc
        self.nodes['sensor']['pressure']    = self.nodes['sensors']['BMP180'].pressure
        self.nodes['sensor']['luminosity']  = self.nodes['sensors']['TSL2561'].luminosity

        if verbose:
            self.detect_nodes()

    def __iter__(self):
        self.sensor_keys = list(self.nodes['sensor'].keys())
        return self

    def __next__(self):
        if len(self.sensor_keys) >= 1:
            tmp_key = self.sensor_keys.pop()
            return tmp_key, self.nodes['sensor'][tmp_key]()
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.nodes['sensor'][key]()

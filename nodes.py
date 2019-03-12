class Nodes:
    """
    Nomenclature
    sensor_id       : e.g. 'BMP180'
    sensor_property : e.g. 'temperature'
    sensor_func     : function e.g. 'temperature', which when called as
                      e.g. 'temperature()' returns readout

    Addition of nodes:
    Can be added in the form of a Sensor object, e.g
    Nodes.add(BMP180_i2c(i2c)) or
    Nodes.add(BMP180_i2c(i2c)).add(SGP30_i2c(i2c))

    Accessing sensor values and sensor objects:
    1) direct iteration on Nodes object, which returns 'sensor_property' and
    'sensor_func' as tuple
    2) using index: 'Nodes[sensor_id]' (returns corresponding object) or
    'Nodes[sensor_property]' (returns sensor_func) e.g. Nodes['BMP180'] or
    Nodes['temperature']
    3) by calling relevant function using attribute style, i.e 'Nodes.sensor_id'
    or 'Nodes.sensor_property()', e.g. Nodes.BMP180 or Nodes.temperature()
    """

    def __init__(self):
        self.nodes = {'sensors' : {}, 'sensor' : {}}

    def add(self, node):
        if 'sensor' in node.info:
            self.nodes['sensors'][node.info['sensor']] = node
            self.nodes['sensor'].update(node.info['readout'])
        return self

    @property
    def connected(self):
        return {key : self.nodes['sensors'][key].connected for
                key in self.nodes['sensors']}

    def __iter__(self):
        self.sensor_keys = list(self.nodes['sensor'].keys())
        return self

    def __next__(self):
        if len(self.sensor_keys) >= 1:
            tmp_key = self.sensor_keys.pop()
            return tmp_key, self.nodes['sensor'][tmp_key]
        else:
            raise StopIteration

    def __getitem__(self, key):
        if key in self.nodes['sensors']:
            return self.nodes['sensors'][key]
        elif key in self.nodes['sensor']:
            return self.nodes['sensor'][key]
        else:
            return None

    def __getattr__(self, key):
        return self.__getitem__(key)

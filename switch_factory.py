from machine import Pin
from tm1637 import TM1637Decimal

class SwitchFactory:

    def display(self, inpt):
        """
        takes as input dict of the form
        {'value' : int/float/str [,'state' : True/False]}
        i.e. the same format as returned by SensorFactory
        alternative an int, float or dict
        """

        if isinstance(inpt, dict):
            if 'state' in inpt:
                if inpt['state']:
                    self.tmdec.brightness(self.switch_set['display']['brightness'])
                else:
                    self.tmdec.brightness(0)
            inpt = inpt.get('value', ' err')

        if isinstance(inpt, int):
            self.tmdec.show('{:4d}'.format(inpt))
        elif isinstance(inpt, float):
            self.tmdec.show('{:5.1f}'.format(inpt))
        elif isinstance(inpt, str):
            self.tmdec.show(inpt)

    def __init__(self, switch_settings):
        """
        takes as argument a dict containing settings for the various switches
        """
        self.switch_set = switch_settings

        # instantiate RobotDyn 4-digit display object
        self.tmdec = TM1637Decimal(Pin(self.switch_set['display']['clk_pin']),
                                   Pin(self.switch_set['display']['dio_pin']))
        self.tmdec.brightness(self.switch_set['display']['brightness'])

        # dictionary containing class methods
        self.switches = {}
        self.switches['display'] = self.display

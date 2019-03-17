from tm1637 import TM1637Decimal
from machine import Pin
import functools

class TM1637Display(TM1637Decimal):
    def __init__(self, clk_pin = 2, dio_pin = 0, brightness = 7):
        super().__init__(Pin(clk_pin), Pin(dio_pin), brightness)
        self.show('    ')
        self.display_func = None

    def add_display_func(self, func, *args, **kwargs):
        """
        takes as argument function(), which when called returns value
        that can be displayed when calling show() without argument
        """
        self.display_func = functools.partial(func, *args, **kwargs)

    def brightness(self, val):
        super().brightness(val)

    def show(self, output = None, *args, **kwargs):
        """
        1.
        takes as argument a dict of the form
        {'value' : int/float/str [,'brightness' : value]}
        i.e. the same format as returned by SensorFactory
        2.
        takes as argument an int, float or string
        3.
        takes as argument a function(), which when called returns value
        according to 1. or 2. that can be displayed
        """

        if output == None and self.display_func:
            try:
                output = self.display_func()
            except:
                output = ' err'
        elif callable(output):
            try:
                output = output(*args, **kwargs)
            except:
                output = ' err'

        if isinstance(output, dict):
            if 'brightness' in output:
                super().brightness(output['brightness'])
            output = output.get('value', ' err')

        if isinstance(output, int):
            super().show('{:4d}'.format(output))
        elif isinstance(output, float):
            super().show('{:5.1f}'.format(output))
        elif isinstance(output, str):
            super().show(output)

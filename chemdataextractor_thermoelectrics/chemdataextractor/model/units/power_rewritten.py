#rewrite power to see if the extra sentence after unit problem persists
from chemdataextractor.model.units import QuantityModel, Unit
from chemdataextractor.model.units.dimension import Dimension
from chemdataextractor.parse.elements import R

class Power2(Dimension):
    pass
    #pass instead of constituent dimensions

class PowerModel2(QuantityModel):

    dimensions = Power2()


class PowerUnit2(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(PowerUnit2, self).__init__(Power2(), magnitude, powers)


class Watt(PowerUnit2):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('(W|w)(att(s)?)?', group=0): Watt}
Power2.units_dict.update(units_dict)
Power2.standard_units = Watt()


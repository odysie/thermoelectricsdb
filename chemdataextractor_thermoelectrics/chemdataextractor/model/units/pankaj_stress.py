from chemdataextractor.model.units import QuantityModel, Unit
from chemdataextractor.model.units.dimension import Dimension
from chemdataextractor.parse.elements import R


class Stress(Dimension):
    """
    Dimension subclass for Stress related quantites.
    """

    pass


class StressModel(QuantityModel):
    """
    Model for stress quantities
    """

    dimensions = Stress()


class StressUnit(Unit):
    """
    Base class for units with dimensions of stress. The standard value is
    Pascal (Pa)
    """

    def __init__(self, magnitude=0.0, powers=None):
        super(StressUnit, self).__init__(Stress(), magnitude, powers)


class Pascal(StressUnit):
    """
    Class for Pascal unit. Since it is the standard no conversion need to be
    defined.
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R("Pa\.?", group=0): Pascal, R("P | a", group=0): None}
Stress.units_dict = units_dict
Stress.standard_units = Pascal()
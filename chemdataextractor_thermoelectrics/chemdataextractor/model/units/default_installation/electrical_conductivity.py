# -*- coding: utf-8 -*-
"""
Units and models for electrical conductivity (σ) for units of [Ω-1 m-1]

Odysseas Sierepeklis <os403@cam.ac.uk>

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from .electrical_resistance import ElectricalResistance
from .electrical_conductance import ElectricalConductance
from .length import Length
from .current import ElectricalCurrent
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join
import logging

class ElectricalConductivity(Dimension):
    constituent_dimensions = (ElectricalResistance() * Length()) ** (-1)
    #since this will catch the per ohm per meter, use resistance as constituent dimensions

class ElectricalConductivityModel(QuantityModel):
    dimensions = ElectricalConductivity()

class ElecricalConductivityUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None): #{ElectricalResistance():-1.0, Length(): -1.0}):
        super(ElecricalConductivityUnit, self).__init__(ElectricalConductivity(), magnitude, powers)

class PerOhmPerMeter(ElecricalConductivityUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


#is this necessary? having 2 classes for possibility of switching constituent units around? Feels like an overkill
class PerMeterPerOhm(ElecricalConductivityUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


#should I just have units, without powers?
#don't use $ and remember to set group = 0
units_dict = {R('(Ω|Ω|(Ohms?))-1( )?m-1', group = 0): PerOhmPerMeter,
              R('m-1( )?(Ω|Ω|(Ohms?))-1', group = 0): PerMeterPerOhm}
              #R('Sm−1', group = 0): SiemensPerMeter}

ElectricalConductivity.units_dict.update(units_dict)
ElectricalConductivity.standard_units = PerOhmPerMeter()
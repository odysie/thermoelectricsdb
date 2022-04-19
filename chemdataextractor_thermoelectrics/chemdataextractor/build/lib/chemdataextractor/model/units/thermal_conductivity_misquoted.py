# -*- coding: utf-8 -*-
"""
Units and models for MISSQUOTED thermal conductivity (κ), quoted as [W / mK] instead of the correct W / m / K.
#NEED TO TAG THESE ONES SOMEHOW, OR FIX THE POST-PROCESSING

Odysseas Sierepeklis <os403@cam.ac.uk>

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from .power import Power
from .length import Length
from .temperature import Temperature
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join
import logging

#NOTE: These units are essentially, WRONG, but they do represent what appears in the literature, i.e. W/mK meaning W/m/K
class ThermalConductivity_misquoted(Dimension):
    constituent_dimensions = Power() * (Length() ** (-1) ) * Temperature()

class ThermalConductivityModel_misquoted(QuantityModel):
    dimensions = ThermalConductivity_misquoted()

class ThermalConductivityUnit_misquoted(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(ThermalConductivityUnit_misquoted, self).__init__(ThermalConductivity_misquoted(), magnitude, powers)


class WattsOverMeterKelvin(ThermalConductivityUnit_misquoted):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


#don't use $ and remember to set group = 0
units_dict = {R('W\/?\(?mK\)?', group = 0): WattsOverMeterKelvin}

ThermalConductivity_misquoted.units_dict.update(units_dict)
ThermalConductivity_misquoted.standard_units = WattsOverMeterKelvin()
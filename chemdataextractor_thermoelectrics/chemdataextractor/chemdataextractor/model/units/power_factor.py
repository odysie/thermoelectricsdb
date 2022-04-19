# -*- coding: utf-8 -*-
"""
Units and models for power factor (PF) in units of [W m-1 K-2]

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

class PowerFactor(Dimension):
    constituent_dimensions = Power() * ( (Length() * (Temperature() ** 2)) ** (-1) )

class PowerFactorModel(QuantityModel):
    dimensions = PowerFactor()

class PowerFactorUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(PowerFactorUnit, self).__init__(PowerFactor(), magnitude, powers)

class WattsPerMeterPerSquaredKelvin(PowerFactorUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('W( )?m-1( )?K-2', group = 0): WattsPerMeterPerSquaredKelvin}

PowerFactor.units_dict.update(units_dict)
PowerFactor.standard_units = WattsPerMeterPerSquaredKelvin()
# -*- coding: utf-8 -*-
"""
Units and models for power factor (PF) MISQUOTED in units of [W m-1 K2] instead of [W m-1 K-2]
works, but not for the things I want it to, such as W/mK2 because it thinks m is mili...

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

class PowerFactorMQ(Dimension):
    constituent_dimensions = Power() * (Length() ** (-1)) * ((Temperature() ** 2))

class PowerFactorModelMQ(QuantityModel):
    dimensions = PowerFactorMQ()

class PowerFactorMQUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(PowerFactorMQUnit, self).__init__(PowerFactorMQ(), magnitude, powers)

class WattsPerMeterKelvinSquared(PowerFactorMQUnit):

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
units_dict = {R('W/mK2', group = 0): WattsPerMeterKelvinSquared}

PowerFactorMQ.units_dict.update(units_dict)
PowerFactorMQ.standard_units = WattsPerMeterKelvinSquared()
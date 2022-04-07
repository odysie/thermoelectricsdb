# -*- coding: utf-8 -*-
"""
Units and models for temperatures.

:codeauthor: Odysseas Sierepeklis (os403@cam.ac.uk)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .quantity_model import QuantityModel, StringType
from .unit import Unit
from .dimension import Dimension
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join

log = logging.getLogger(__name__)


class Pressure(Dimension):
    """
    Dimension subclass for pressures.
    """
    pass


class PressureModel(QuantityModel):

    dimensions = Pressure()


class PressureUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(PressureUnit, self).__init__(Pressure(), magnitude, powers)


class Pascal(PressureUnit):
    """
    Class for Pascals.
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


class Atmospheres(PressureUnit):
    """
    Class for Atmospheres
    """

    def convert_value_to_standard(self, value):
        return value * 101325

    def convert_value_from_standard(self, value):
        return value * 101325

    def convert_error_to_standard(self, error):
        return error * 101325

    def convert_error_from_standard(self, error):
        return error * 101325


units_dict = {R('Pa(?:scals?)?$', group=0): Pascal,
              R('atm', group=0): Atmospheres}

Pressure.units_dict = units_dict
Pressure.standard_units = Pascal()

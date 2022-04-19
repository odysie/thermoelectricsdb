# -*- coding: utf-8 -*-
"""
Units and models for Seebeck coefficient.

Note that some extractions don't work as expected (e.g. VK-1).
Can use bespoke function to change units prior to parsing.
Might also try commenting out constituent_diemnsions in electric_potential.py, for some reason.

Odysseas Sierepeklis <os403@cam.ac.uk>

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from .electric_potential import ElectricPotential
from .temperature import Temperature
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
import logging
log = logging.getLogger(__name__)


class SeebeckCoefficient(Dimension):
    constituent_dimensions = ElectricPotential() / Temperature()


class SeebeckCoefficientModel(QuantityModel):
    dimensions = SeebeckCoefficient()


class SeebeckCoefficientUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(SeebeckCoefficientUnit, self).__init__(SeebeckCoefficient(), magnitude, powers)


class VoltsPerKelvin(SeebeckCoefficientUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


class KelvinPerVolts(SeebeckCoefficientUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('V( )?K-1', group = 0): VoltsPerKelvin,
              R('K-1( )?V', group = 0): KelvinPerVolts}

SeebeckCoefficient.units_dict.update(units_dict)
SeebeckCoefficient.standard_units = VoltsPerKelvin()


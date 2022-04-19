# -*- coding: utf-8 -*-
"""
Units and models for electrical resistivity (ρ) in units of [Ωm]
# following Taketomo Isazawa's <ti250@cam.ac.uk> quantity.py update, mΩ works fine (no more meter - mili problem)

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
from .length import Length
from .current import ElectricalCurrent
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join
import logging

class ElectricalResistivity(Dimension):
    constituent_dimensions = ElectricalResistance() * Length()

class ElectricalResistivityModel(QuantityModel):
    dimensions = ElectricalResistivity()

class ElectricalResistivityUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(ElectricalResistivityUnit, self).__init__(ElectricalResistivity(), magnitude, powers)

class OhmMeter(ElectricalResistivityUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


class MeterOhm(ElectricalResistivityUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


#CDE on its own doesn't caputre mΩ as meter Ohms (confused as mili Ohms), and similarly it doesn't catch cmΩ and  mmΩ.
#with the addition of the MeterOhm in the dictionary, the above cases are caught.
#However, it then fails to catch mΩm and mΩcm, which hopefully are quite rare.

units_dict = {R('m( )?(Ω|Ω|(Ohms?))', group = 0): MeterOhm}
ElectricalResistivity.units_dict.update(units_dict)
ElectricalResistivity.standard_units = OhmMeter()
# -*- coding: utf-8 -*-
"""
Units and models for electrical resistance (R) in units of [Ω]

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
from .current import ElectricalCurrent
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join
import logging

log = logging.getLogger(__name__)

#pass, no constituent dimensions used for quoting
class ElectricalResistance(Dimension):
    pass

class ElectricalResistanceModel(QuantityModel):
    dimensions = ElectricalResistance()


class ElectricalResistanceUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(ElectricalResistanceUnit, self).__init__(ElectricalResistance(), magnitude, powers)


class Ohm(ElectricalResistanceUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('Ω|Ω|(Ohm(s)?)', group = 0): Ohm}

# set units dict, since there are no constituent diemnsions
ElectricalResistance.units_dict = units_dict
ElectricalResistance.standard_units = Ohm()


# -*- coding: utf-8 -*-
"""
Units and models for electrical conductance (G) in units of [S]

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


#uses siemens, so no
class ElectricalConductance(Dimension):
    pass


class ElectricalConducatnceModel(QuantityModel):
    dimensions = ElectricalConductance()


class ElectricalConductanceUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(ElectricalConductanceUnit, self).__init__(ElectricalConductance(), magnitude, powers)


class Siemens(ElectricalConductanceUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('S(iemens)?', group = 0): Siemens}

# since this is not a composite dimension, simply set the unit
ElectricalConductance.units_dict = units_dict
ElectricalConductance.standard_units = Siemens()


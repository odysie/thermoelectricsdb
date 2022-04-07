from chemdataextractor.parse.quantity import value_element, value_element_plain, extract_value
import chemdataextractor.parse.quantity
from chemdataextractor.model import TemperatureModel, Compound, ModelType, StringType
from chemdataextractor.parse.auto import *
from chemdataextractor.parse.elements import NoMatch
from chemdataextractor.doc.text import Sentence
from chemdataextractor.model.units import DimensionlessModel
from pprint import pprint
from chemdataextractor import Document
from chemdataextractor.doc import Paragraph

from chemdataextractor.model.units.electrical_resistance import ElectricalResistanceModel
from chemdataextractor.model.units.electrical_conductance import ElectricalConducatnceModel
from chemdataextractor.model.units.electrical_resistivity import ElectricalResistivityModel
from chemdataextractor.model.units.electrical_conductivity import ElectricalConductivityModel
from chemdataextractor.model.units.electrical_conductivity2 import ElectricalConductivityModel2
from chemdataextractor.model.units.thermal_conductivity import ThermalConductivityModel
from chemdataextractor.model.units.thermal_conductivity_misquoted import ThermalConductivityModel_misquoted
from chemdataextractor.model.units.Seebeck_coefficient import SeebeckCoefficientModel
from chemdataextractor.model.units.power_factor import PowerFactorModel
from chemdataextractor.model.units.pressure import PressureModel

from chemdataextractor.parse.template import QuantityModelTemplateParser, MultiQuantityModelTemplateParser
from lxml import etree

#new change:
from chemdataextractor.parse.expressions_for_models import processing_expression, direction_expression, contextual_label_expression, editing_expression

import re


#oddy (from Taketomo's code)
# notes on restriction ranges: used to be a global variable RANGE (from Take's quick code). Changed it into a model-specific
# variable, so that it can have different values for each model. It is first defined as restriction_range in a model.
# The original definition is None, in QuanityModel, so it is available to MASP via self.model.restriction_range.
# There is an if statement to check if it is defined, and if so, then it is applied.

def restrict_value_range(value_range):
    #value_range is going to be a tuple
    def _internal(result):
        for el in result:
            if el.tag == "raw_value":
                raw_value = el.text
                value = extract_value(raw_value)
                if len(value) == 1:
                    value = [value[0], value[0]]
                if value[0] > value_range[0] and value[1] < value_range[1]:
                    return True
        return False
    return _internal

#redefines a new versions of value_element and value_element_plain, with the restriction condition applied
#value_element "Returns an Element for values with given units. By default, uses tags to guess that a unit exists."
#value_element_plain "Returns an element similar to value_element but without any units."
def new_value_element(limit, *args, **kwargs):
    element = value_element(*args, **kwargs).with_condition(restrict_value_range(limit))
    return element


def new_value_element_plain(my_range, *args, **kwargs):
    element = value_element_plain(*args, **kwargs).with_condition(restrict_value_range(my_range))
    return element


class MyAutoSentenceParser(AutoSentenceParser):

    @property
    def root(self):
        #oddy:
        restriction_range = self.model.restriction_range
        #print(f"this is the restriction range: {restriction_range} for {self.model}")

        # is always found, our models currently rely on the compound
        chem_name = self.chem_name
        compound_model = self.model.compound.model_class    #get the model(?)
        labels = compound_model.labels.parse_expression('labels')
        entities = [labels]

        #distinguish between Dimensionless model and Quantity model
        if hasattr(self.model, 'dimensions') and not self.model.dimensions:
            # the mandatory elements of Dimensionless model are grouped into a entities list
            specifier = self.model.specifier.parse_expression('specifier')
            if restriction_range:   #if restriction_range different to none, then use the new definitions, which employ restrictions
                value_phrase = new_value_element_plain(restriction_range)
            else:
                value_phrase = value_element_plain() #normal ASP
            entities.append(specifier)
            entities.append(value_phrase)

        elif hasattr(self.model, 'dimensions') and self.model.dimensions:
            # the mandatory elements of Quantity model are grouped into a entities list
            # print(self.model, self.model.dimensions)
            unit_element = Group(
                construct_unit_element(self.model.dimensions).with_condition(match_dimensions_of(self.model))('raw_units'))
            specifier = self.model.specifier.parse_expression('specifier')
            if restriction_range:
                if self.lenient:
                    value_phrase = (new_value_element(restriction_range, unit_element) | new_value_element_plain())
                else:
                    value_phrase = new_value_element(restriction_range, unit_element)
            else: #normal ASP
                if self.lenient:
                    value_phrase = (value_element(unit_element) | value_element_plain())
                else:
                    value_phrase = value_element(unit_element)

            entities.append(specifier)
            entities.append(value_phrase)

        elif hasattr(self.model, 'specifier'):
            # now we are parsing an element that has no value but some custom string
            # therefore, there will be no matching interpret function, all entities are custom except for the specifier
            specifier = self.model.specifier.parse_expression('specifier')
            entities.append(specifier)

        # the optional, user-defined, entities of the model are added, they are tagged with the name of the field
        for field in self.model.fields:
            if field not in ['raw_value', 'raw_units', 'value', 'units', 'error', 'specifier']:
                if self.model.__getattribute__(self.model, field).parse_expression is not None:
                    entities.append(self.model.__getattribute__(self.model, field).parse_expression(field))

        # the chem_name has to be parsed last in order to avoid a conflict with other elements of the model
        entities.append(chem_name)

        # logic for finding all the elements in any order
        combined_entities = create_entities_list(entities)
        root_phrase = OneOrMore(combined_entities + Optional(SkipTo(combined_entities)))('root_phrase')
        return root_phrase





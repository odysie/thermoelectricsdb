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
from .auto_old import AutoSentenceParser_Old
from chemdataextractor.parse.template import QuantityModelTemplateParser
from lxml import etree

import re

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

##########
#NOTE: Ignore restriction values for now, except for zt. Keep AutoSentenceParser (which fixes meter-mili problem and allows 'room temperature extraction'), and NOT AutoSentenceParser_Old
##########

#recent: added above
class Temperature(TemperatureModel):
    specifier_expression =(I('temperature') | W('T') | I('at') | I('near') | I('around') | I('above'))
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    #restriction_range = (300,1000) #this works, but not a big reason to have it with temperature, also it might have problems between K and C
    parsers = [AutoSentenceParser()]


#not used now
class doping_percentage(DimensionlessModel):
    specifier = StringType(parse_expression=W('%'), required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    parsers = [AutoSentenceParser()]
    #make a specific parser only grabs number if followed by % sign


#not used now
class Resistance(ElectricalResistanceModel):
    specifier_expression = ((I('electrical') + I('resistance')) | W('R')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser_Old()]    #super hacky solution. New ASP (with [variable?] restrictions seems to fail for Seebeck coefficient, so i defined ASP_Old which inherists from quantity_old.py)


#not used now
class Conductance(ElectricalConducatnceModel):
    specifier_expression = ((I('electrical') + I('conductance')) | W('G')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser_Old()]    #super hacky solution. New ASP (with [variable?] restrictions seems to fail for Seebeck coefficient, so i defined ASP_Old which inherists from quantity_old.py)


#try without specifying electrical, thermal, etc. and see if the units do the job well enough. Extend the specifier_expressions a bit
class Resistivity(ElectricalResistivityModel):
    specifier_expression = (I('resistivity') | W('ϱ') | W('ρ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]    #AutoSentenceParser_Old FAILS WITH THINGS LIKE mΩ. Need to use AutoSentenceParser to distinguish mΩ as meter Ohms!


class Conductivity(ElectricalConductivityModel):    #per Ohm per meter
    specifier_expression = (I('conductivity') | W('σ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]


class Conductivity2(ElectricalConductivityModel2):  #Siemens per meter
    specifier_expression = (I('conductivity') | W('σ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]

    #have a better look at the specifier

class ThermCond(ThermalConductivityModel):
    specifier_expression = ( (Optional(R('electron') | R('lattice') | R('phonon')) + I('thermal') + R('conductiv')) | R('^κ_?([EeLlPpTtCc](\S*))?$') | R('^λ_?([EeLlPpTtCc](\S*))?$') | R('^k_([EeLlPpTtCc](\S*))?$')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    preceeding_edited_with = (Optional(R('alloy.+|doped|doping|prepar.+|added|adding|treat.+|fill.+|deficient|substitut.+')) + Optional(R('with'))).add_action(join)
    editing_expression = (preceeding_edited_with + W('**') + W('%') + Optional(T('B-CM')) + ZeroOrMore(T('I-CM'))).add_action(join)
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)

    room_temperature_expression = (R('^r\.?t\.?$', re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]


#This is new. POWER FACTOR
class PF(PowerFactorModel):
    specifier_expression = ( (I('power') + I('factor')) | I('pf') | I('p.f.') | I('κZT') | I('ZTκ') | R('σα2') | R('σS2') | R('α2σ') | R('S2σ') ).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$', re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]


#will probably not use. HAVEN'T EVEN ADDED ROOM TEMP EXTRACTION
class ThermCond_misquoted(ThermalConductivityModel_misquoted):
    specifier_expression = ((Optional(I('lattice') | R('^electron?(ic)?$')) + I('thermal') + I('conductivity')) | W('κ') | W('k') | W('λ') | R('κ_?e') | R('κ_?[plL]')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False
    parsers = [AutoSentenceParser()]


class Seebeck(SeebeckCoefficientModel):
    specifier_expression = ((I('Seebeck') + I('coefficient')) | I('thermopower') | (I('thermoelectric') + I('power')) | (I('thermoelectric') + I('sensitivity')) | W('S') | W('α')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser()]


class ZT(DimensionlessModel):
    specifier_expression =((R('^figures?$', re.I) + I('of') + I('merit')) | I('zt')  | I('ztmax') | R('^[Ff]\.?[Oo]\.?[Mm]$')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    restriction_range = (0,3)
    parsers = [MyAutoSentenceParser()]

class ZT_NEW(DimensionlessModel):
    specifier_expression =((R('^figures?$', re.I) + I('of') + I('merit')) | I('zt') | R('^[Ff]\.?[Oo]\.?[Mm]$')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature_expression = (R('^r\.?t\.?$',re.I) | (I('room') + Optional(T('HYPH')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    #if the synthesis method is part of the CEM, e.g. hot-pressed BiCuSeO, it will be extracted only in the synthesis field, and not as part of the name like it used to
    synthesis_expression = (R('ball|hot|arc|spark') + Optional(T('HYPH')) + Optional(R('plasma')) + Optional(T('HYPH')) + R('sinter.+|mill.+|anneal.+|press.+')).add_action(join) #don't forget the add_action to join
    synthesis = StringType(parse_expression=synthesis_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    restriction_range = (0,3)
    parsers = [MyAutoSentenceParser()]


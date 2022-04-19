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

from chemdataextractor.parse.auto_default import AutoSentenceParser_Old
from chemdataextractor.parse.restrict_values_new import MyAutoSentenceParser
from chemdataextractor.parse.template import QuantityModelTemplateParser, MultiQuantityModelTemplateParser
from lxml import etree

# -*- coding: utf-8 -*-
"""
Units and models for power factor (PF) in units of [W m-1 K-2]

Odysseas Sierepeklis <os403@cam.ac.uk>

"""

#new change:
from chemdataextractor.parse.expressions_for_models import processing_expression, direction_expression, contextual_label_expression, editing_expression

import re

##########
#NOTE: Ignore restriction values for now, except for zt. Keep AutoSentenceParser (which fixes meter-mili problem and allows 'room temperature extraction'), and NOT AutoSentenceParser_Old
##########

#recent: added 'above'
class Temperature(TemperatureModel):
    specifier_expression = (I('temperature') | W('T') | I('at') | I('near') | I('around') | I('above'))
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    #restriction_range = (300,1000) #this works, but not a big reason to have it with temperature, also it might have problems between K and C
    parsers = [AutoSentenceParser()]


# v7 added Pressure
# no specifier to avoid contradicitons with temperature?
class Pressure(PressureModel):
    pressure_specifier_expression = (W('at') | W('near') | W('under') | (Optional(W('ambient') | W('room')) + W('pressure'))).add_action(join)
    specifier = StringType(parse_expression= pressure_specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
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


#USEFULL expressions
#new change: global variable for room temperature expression, added ambient, deleted all the ones inside models, since they now take from here
room_temperature_expression = (R('^r\.?t\.?$',re.I) | ((I('room')|I('ambient')) + Optional(I('-')) + I('temperature'))).add_action(join)
#new change: added the specifier prefix. just added optimal
# v5 added type in specifier prefix
specifier_prefix = (R('max|min|peak|highest|avg|average|mean|optimal|film|bulk') | (R('^[np]$') + Optional(Optional(T('HYPH')) + W('type')))).add_action(join)
specifier_suffix = R('max|min|avg|mean|⊥|//') | (W('/') + W('/')).add_action(merge)  # last part because parallel: // broken up in two symbols

#try without specifying electrical, thermal, etc. and see if the units do the job well enough. Extend the specifier_expressions a bit
class Resistivity(ElectricalResistivityModel):
    specifier_expression = ( Optional(specifier_prefix) + (I('resistivity') | W('ϱ') | W('ρ'))
                             + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]    #AutoSentenceParser_Old FAILS WITH THINGS LIKE mΩ. Need to use AutoSentenceParser to distinguish mΩ as meter Ohms!


class Conductivity(ElectricalConductivityModel):    #per Ohm per meter
    #recent change, W('σ') changed to (W('σ') + Not(W('/'))) in order to protect from σ/τ things and added optional ionic and specifier prefix
    specifier_expression = ( Optional(specifier_prefix) + (Optional(R('ion(?:ic)?|electric(?:al)?', re.I)) + I('conductivity') | (W('σ') + Not(W('/'))))
                             + Optional(specifier_suffix) ).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


class Conductivity2(ElectricalConductivityModel2):  #Siemens per meter
    #recent change, W('σ') changed to (W('σ') + Not(W('/'))) in order to protect from σ/τ things and added optional ion(ic) and specifier prefix. Changed I('conductivity') to more general regex
    specifier_expression = ( Optional(specifier_prefix) + (Optional(R('ion(?:ic)?|electric(?:al)?', re.I)) + R('conductivit') | (W('σ') + Not(W('/'))))
                             + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]

    #have a better look at the specifier


class ThermCond(ThermalConductivityModel):
    #recent change specifier prefix
    specifier_expression = ( Optional(specifier_prefix) + ( (Optional(R('electron') | R('lattice') | R('phonon')) + I('thermal') + R('conductiv')) |
                             R('^κ_?([EeLlPpTtCc](\S*))?$') | R('^λ_?([EeLlPpTtCc](\S*))?$') | R('^k_([EeLlPpTtCc](\S*))?$'))
                             + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    # NB editing needs to come before process. E.g. Following allowing with BaMg2Bi2, our sample showed ZT of 1.2 at 300K.
    # This should return 0 records, and it does, if the editing preceeds the process.
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


# v4 for some reason compound required was set to False...
#This is new. POWER FACTOR
class PF(PowerFactorModel):
    # v8 changed I('pf') to R('^pf', re.I) which capture
    #new addition for S2/ρ types. Transfer to TDE models as well. specifier prefix
    pf_specifier_expression = (Optional(specifier_prefix) + ((I('power') + R('factors?')) | R('^pf⊥?', re.I) | I('p.f.') | I('κZT') |
                                                          I('ZTκ') | R('σα\^?2') | R('σS\^?2') | R('α\^?2σ') | R('S\^?2σ') |
                                                             ((R('S\^?2')|R('α\^?2')) + W('/') + W('ρ')))
                               + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=pf_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


#This is even newer, v6, to account for annoying W/mK2 -style PF units
from chemdataextractor.model.units.power_factor_misquoted import PowerFactorModelMQ
class PFMQ(PowerFactorModelMQ):
    #new addition for S2/ρ types. Transfer to TDE models as well. specifier prefix
    pf_specifier_expression = (Optional(specifier_prefix) + ((I('power') + R('factors?')) | I('pf') | I('p.f.') | I('κZT') |
                                                          I('ZTκ') | R('σα2') | R('σS2') | R('α2σ') | R('S2σ') | ((W('S2')|W('α2')) + W('/') + W('ρ'))) ).add_action(join)
    specifier = StringType(parse_expression=pf_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

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
    specifier_expression = (Optional(specifier_prefix) + ((I('Seebeck') + I('coefficient')) | I('thermopower')
                                | (I('thermoelectric') + I('power')) | (I('thermoelectric')
                                + I('sensitivity')) | W('S') | W('α')) + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


#THIS IS THE NEW VERSION OF ZT

class ZT(DimensionlessModel):
    specifier_expression = (Optional(specifier_prefix) + ((R('^figures?$', re.I) + I('of') + I('merit')) | I('zt')
                                                          | R('^[Ff]\.?[Oo]\.?[Mm]$'))
                            + Optional(specifier_suffix)).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # NB editing should preceed process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    restriction_range = (0, 3)
    parsers = [MyAutoSentenceParser()]

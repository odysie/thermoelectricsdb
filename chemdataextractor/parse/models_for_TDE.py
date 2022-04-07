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


#oddy models for TableDataExtractor


#recent: added above
class Temperature(TemperatureModel):
    specifier_expression =(I('temperature') | W('T') | I('at') | I('near') | I('around') | I('above'))
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    #restriction_range = (300,1000) #this works, but not a big reason to have it with temperature, also it might have problems between K and C
    parsers = [AutoTableParser()] #this is nested in the other models
    #but does it work? for example if a column entry is Pf ~ 350 K will the temperature be picked up??

#how do nested models work with different parsers?

#extract temperature from table captions, including room temperature mentions (which are typically captured by the 5 seminal models)
class Temperature_for_table_captions(TemperatureModel):
    specifier_expression =(I('temperature') | W('T') | I('at') | I('near') | I('around') | I('above'))
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature_expression = (
                R('^r\.?t\.?$', re.I) | (I('room') + Optional(I('-')) + I('temperature'))).add_action(join)
    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    parsers = [AutoSentenceParser()]

#not used now
class doping_percentage(DimensionlessModel):
    specifier = StringType(parse_expression=W('%'), required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    parsers = [AutoSentenceParser()]
    #make a specific parser only grabs number if followed by % sign


#not used now
class Resistance_for_TDE(ElectricalResistanceModel):
    specifier_expression = ((I('electrical') + I('resistance')) | W('R')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser_Old()]    #super hacky solution. New ASP (with [variable?] restrictions seems to fail for Seebeck coefficient, so i defined ASP_Old which inherists from quantity_old.py)


#not used now
class Conductance_for_TDE(ElectricalConducatnceModel):
    specifier_expression = ((I('electrical') + I('conductance')) | W('G')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoSentenceParser_Old()]    #super hacky solution. New ASP (with [variable?] restrictions seems to fail for Seebeck coefficient, so i defined ASP_Old which inherists from quantity_old.py)


#new change:
from .restrict_values_new import room_temperature_expression

#try without specifying electrical, thermal, etc. and see if the units do the job well enough. Extend the specifier_expressions a bit
class Resistivity_for_TDE(ElectricalResistivityModel):
    specifier_expression = (I('resistivity') | W('ϱ') | W('ρ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]    #AutoSentenceParser_Old FAILS WITH THINGS LIKE mΩ. Need to use AutoSentenceParser to distinguish mΩ as meter Ohms!


class Conductivity_for_TDE(ElectricalConductivityModel):    #per Ohm per meter
    specifier_expression = (I('conductivity') | W('σ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]


class Conductivity2_for_TDE(ElectricalConductivityModel2):  #Siemens per meter
    specifier_expression = (I('conductivity') | W('σ')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]

    #have a better look at the specifier

class ThermCond_for_TDE(ThermalConductivityModel):
    specifier_expression = ( (Optional(R('electron') | R('lattice') | R('phonon')) + I('thermal') + R('conductiv')) | R('^κ_?([EeLlPpTtCc](\S*))?$') | R('^λ_?([EeLlPpTtCc](\S*))?$') | R('^k_([EeLlPpTtCc](\S*))?$')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]



#This is new. POWER FACTOR
class PF_for_TDE(PowerFactorModel):
    #new change: S2/ρ types
    specifier_expression = ( (I('power') + I('factor')) | I('pf') | I('p.f.') | I('κZT') | I('ZTκ') | R('σα2') | R('σS2') | R('α2σ') | R('S2σ') | ((W('S2')|W('α2')) + W('/') + W('ρ')) ).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]




#small change for Seebeck coefficient in table extraction vs sentence extraction:
#replaced W('S') with R('^S$') to avoid catching things such as the S for Siemens in the elec cond units
#also added a step in to_pandas.py which replaces the problematic VK-1 type units with V/K which work

class Seebeck_for_TDE(SeebeckCoefficientModel):
    specifier_expression = ((I('Seebeck') + I('coefficient')) | I('thermopower') | (I('thermoelectric') + I('power')) | (I('thermoelectric') + I('sensitivity')) | R('^S$') | R('S~?\d\d\dK') | W('α')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # the entries in in each sell are also split in tokens so we need to add up different rules in  to pick it up
    # but why are the numbers also split up on the fullstop??
    #the two different optionals are necessary e.g. 2% vs. 2.3 vs. 2.3%
    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively
    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]


#THIS IS THE NEW VERSION OF ZT

class ZT_for_TDE(DimensionlessModel):
    specifier_expression =((R('^figures?$', re.I) + I('of') + I('merit')) | I('zt') | R('^[Ff]\.?[Oo]\.?[Mm]$')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    table_label_expression = (R('x') + R('=') + R('\d') + Optional(R('\.') + R('\d')) + Optional(R('%'))).add_action(join)
    table_label = StringType(parse_expression=table_label_expression, required=False, contextual=False) #narrow space unicode /u202F was pasted in exclusively

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    parsers = [AutoTableParser()]



#each plus is to be caught in a tagged token
specifier_temperature = T('-LRB-') + R('^\d\d\d?$') + W('K') + T('-RRB-')

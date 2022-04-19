# -*- coding: utf-8 -*-
"""
Property models for thermoelectric matreials.

Models for all the properties used during data extraction for the thermoelectric materials project.

These include:
    Models being nested:
        Temperature
        Pressure

    Models nesting Temperature and Pressure:
        Resistivity (Electrical Resistivity)
        Conductivity (Electrical Conductivity in dimensions of Ohm ^ (-1) * meter ^ (-1))
        Conductivity2 (Electrical Conductivity in dimensions of Siemens * meter ^ (-1))
        ThermCond (Thermal Conductivity)
        PF (Power Factor)
        Seebeck (Seebeck coefficient)
        ZT (thermoelectric figure of merit)
"""

from chemdataextractor.model import TemperatureModel, Compound, ModelType, StringType
from chemdataextractor.parse.auto import *
from chemdataextractor.model.units import DimensionlessModel
from chemdataextractor.model.units.electrical_resistivity import ElectricalResistivityModel
from chemdataextractor.model.units.electrical_conductivity import ElectricalConductivityModel
from chemdataextractor.model.units.electrical_conductivity2 import ElectricalConductivityModel2
from chemdataextractor.model.units.thermal_conductivity import ThermalConductivityModel
from chemdataextractor.model.units.Seebeck_coefficient import SeebeckCoefficientModel
from chemdataextractor.model.units.power_factor import PowerFactorModel
from chemdataextractor.model.units.pressure import PressureModel

from chemdataextractor.parse.auto_default import AutoSentenceParser_Old
from chemdataextractor.parse.restrict_values_new import RestrictionAutoSentenceParser

from chemdataextractor.parse.expressions_for_models import temperature_specifier_expression, room_temperature_expression, pressure_specifier_expression
from chemdataextractor.parse.expressions_for_models import resistivity_specifier_expression, conductivity_specifier_expression, conductivity2_specifier_expression, thermal_specifier_expression, pf_specifier_expression, seebeck_specifier_expression, zt_specifier_expression
from chemdataextractor.parse.expressions_for_models import processing_expression, direction_expression, contextual_label_expression, editing_expression

# Nested models:
class Temperature(TemperatureModel):
    """Temperature property model"""
    specifier = StringType(parse_expression=temperature_specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    parsers = [AutoSentenceParser()]


# There is an overlap between the pressure and temperature specifiers
# so the pressure model is commented out in the nesting property models.
# In the thermoelectrics project, pressure was extracted individually, after the nesting models.
class Pressure(PressureModel):
    """Pressure property model"""
    specifier = StringType(parse_expression=pressure_specifier_expression, required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)
    parsers = [AutoSentenceParser()]


# Nesting models:

# AutoSentenceParser_Old (from version 2.0.0) fails with things such as mΩ (mili vs. meter).
# Use AutoSentenceParser (updated) to distinguish mΩ as meter Ohms.

class Resistivity(ElectricalResistivityModel):
    """Electrical Resistivity property model"""
    specifier = StringType(parse_expression=resistivity_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    # NB editing should precede process
    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)

    parsers = [AutoSentenceParser()]


class Conductivity(ElectricalConductivityModel):
    """Electrical Conductivity property model in dimensions of Ohm ^ (-1) * meter ^ (-1))"""
    specifier = StringType(parse_expression=conductivity_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


class Conductivity2(ElectricalConductivityModel2):
    """Electrical Conductivity property model in dimensions of Siemens * meter ^ (-1))"""
    specifier = StringType(parse_expression=conductivity2_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=False, contextual=False, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    parsers = [AutoSentenceParser()]


class ThermCond(ThermalConductivityModel):
    """Thermal Conductivity property model"""
    specifier = StringType(parse_expression=thermal_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

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


class PF(PowerFactorModel):
    """Power Factor property model"""
    specifier = StringType(parse_expression=pf_specifier_expression, required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

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


class Seebeck(SeebeckCoefficientModel):
    """Seebeck coefficient property model"""
    specifier = StringType(parse_expression=seebeck_specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)

    parsers = [AutoSentenceParser()]


class ZT(DimensionlessModel):
    """Dimensionless ZT property model"""
    specifier = StringType(parse_expression=zt_specifier_expression, required=True, contextual=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)

    room_temperature = StringType(parse_expression=room_temperature_expression, required=False, contextual=False)

    editing = StringType(parse_expression=editing_expression, required=False, contextual=False)
    process = StringType(parse_expression=processing_expression, required=False, contextual=False)
    direction_of_measurement = StringType(parse_expression=direction_expression, required=False, contextual=False)
    contextual_doping = StringType(parse_expression=contextual_label_expression, required=False, contextual=False)

    temperature = ModelType(Temperature, required=False, contextual=False)
    temperature.model_class.fields['raw_value'].required = False
    temperature.model_class.fields['raw_units'].required = False

    pressure = ModelType(Pressure, required=False, contextual=False)  # would ideally set raw_units to required

    # restriction range for the RestricitonAutoSentenceParser
    restriction_range = (0, 3)
    parsers = [RestrictionAutoSentenceParser()]

# -*- coding: utf-8 -*-
"""
Useful expressions for the definitions of thermoelectric property models.

Includes property specifier expressions, as well as other useful expressions, such as
expressions for process, direction of measurement, and editing.
"""

from chemdataextractor.parse import Optional, R, T, W, I, Not
from chemdataextractor.parse.actions import join, merge
from chemdataextractor.parse.cem import elements_or_string, doping_percentages
import re

# Specifier expressions for thermoelectric property models:
room_temperature_expression = (R('^r\.?t\.?$',re.I) | ((I('room')|I('ambient')) + Optional(I('-')) + I('temperature'))).add_action(join)

# specifier prefixes and suffixes
specifier_prefix = (R('max|min|peak|highest|avg|average|mean|optimal|film|bulk') | (R('^[np]$') + Optional(Optional(T('HYPH')) + W('type')))).add_action(join)
specifier_suffix = R('max|min|avg|mean|⊥|//') | (W('/') + W('/')).add_action(merge)  # last part because parallel: // broken up in two symbols

temperature_specifier_expression = (I('temperature') | W('T') | I('at') | I('near') | I('around') | I('above'))

pressure_specifier_expression = (
            W('at') | W('near') | W('under') | (Optional(W('ambient') | W('room')) + W('pressure'))).add_action(join)

resistivity_specifier_expression = (Optional(specifier_prefix) + (I('resistivity') | W('ϱ') | W('ρ'))
                        + Optional(specifier_suffix)).add_action(join)

conductivity_specifier_expression = (Optional(specifier_prefix) + (
            Optional(R('ion(?:ic)?|electric(?:al)?', re.I)) + I('conductivity') | (W('σ') + Not(W('/'))))
                        + Optional(specifier_suffix)).add_action(join)

conductivity2_specifier_expression = (Optional(specifier_prefix) + (
            Optional(R('ion(?:ic)?|electric(?:al)?', re.I)) + R('conductivit') | (W('σ') + Not(W('/'))))
                        + Optional(specifier_suffix)).add_action(join)

thermal_specifier_expression = (Optional(specifier_prefix) + (
            (Optional(R('electron') | R('lattice') | R('phonon')) + I('thermal') + R('conductiv')) |
            R('^κ_?([EeLlPpTtCc](\S*))?$') | R('^λ_?([EeLlPpTtCc](\S*))?$') | R('^k_([EeLlPpTtCc](\S*))?$'))
                        + Optional(specifier_suffix)).add_action(join)

pf_specifier_expression = (
            Optional(specifier_prefix) + ((I('power') + R('factors?')) | R('^pf⊥?', re.I) | I('p.f.') | I('κZT') |
                                          I('ZTκ') | R('σα\^?2') | R('σS\^?2') | R('α\^?2σ') | R('S\^?2σ') |
                                          ((R('S\^?2') | R('α\^?2')) + W('/') + W('ρ')))
            + Optional(specifier_suffix)).add_action(join)

seebeck_specifier_expression = (Optional(specifier_prefix) + ((I('Seebeck') + I('coefficient')) | I('thermopower')
                                                      | (I('thermoelectric') + I('power')) | (I('thermoelectric')
                                                                                              + I('sensitivity')) | W(
            'S') | W('α')) + Optional(specifier_suffix)).add_action(join)

zt_specifier_expression = (Optional(specifier_prefix) + ((R('^figures?$', re.I) + I('of') + I('merit')) | I('zt')
                                                      | R('^[Ff]\.?[Oo]\.?[Mm]$'))
                        + Optional(specifier_suffix)).add_action(join)

# More expressions:
single_temp_or_pressure = ((R('high|low') + Optional(T('HYPH')) + R('temperature|pressure')) | R('^[HL][TP](?:[HL][TP])?$'))
qualitative_temp_or_pressure = single_temp_or_pressure + Optional(Optional(W('and')) + single_temp_or_pressure)

simple_processing = (Optional(R('ball|hot|cold|melt|arc|spark|mechanical|drop|vapour|laser|3D|powder|acid|screen')) + Optional(T('HYPH')) +
                         Optional(R('plasma')) + Optional(T('HYPH')) +
                         R('sinter|mill|drill|deposit|anneal|alloy|press|spun|spin|deform|process|fabri|cast|forg|roll|weld|extru|clad|print|mold|treat|quench')).add_action(merge)

processing_abbreviation = R('^(?:SPS|L?P?CVD|SILAR|P?LD)$') + Optional(Optional(T('HYPH')) + R('press'))

at_temperature_or_pressure = R('at') + T('CD') + (W('°C') | (Optional(R('°')) + R('[GkK]Pa(?:scals)?|k?bar|°?(((K|k)elvin(s)?)|K)\.?|(°C|((C|c)elsius))\.??')))  #sometimes '°C' is split sometimes not (?)

# just qualitative
# or processing, with optional temperature or pressure
# or just at a certain pressure
processing_expression = (qualitative_temp_or_pressure | ((processing_abbreviation |
                          simple_processing + Optional(R('^and|with|plus$') + simple_processing)) + Optional(at_temperature_or_pressure))
                         | (R('at') + T('CD') + R('[GkK]Pa(?:scals)?|k?bar'))).add_action(join)

axes = (R('[xyzabc][xyzabc]?') + Optional(T('HYPH')) + R('axis|direction') | R('[xyzabc][xyzabc]?.?(?:ax[ie]s|directions?)') | (R('[xyzabc]') + R('^and$') + R('[xyzabc]') + R('axes|directions')))
crystallographic_direction = R('[\[\(][01][01][01][\)\]]') + R('direction|plane')
planes = R('in|out') + Optional(T('HYPH')) + Optional(R('of') + Optional(T('HYPH'))) + R('plane')
relative_to_process = R('perpendicular|parallel') + W('to') + W('the') + Optional(W('direction') + W('of')) + (processing_abbreviation | simple_processing)

direction_expression = (axes | planes | crystallographic_direction | relative_to_process).add_action(join)

contextual_label_expression = ( R('x|y') + R('^[=><≥≤]$') + T('CD') ).add_action(join)

ce = R('[A-Z][a-z]*\d*|\([^)]+\)\d*')
# only for verbs or nouns, no adjectives!
editing_action = R('(?:substitut|inclu[sd]|incorporat|alloy|add(?:it)?|introduct?|dop)(?:ing|ion)')  # NB: this has to be such that it doesn't start tagging 'doped' or else we lose Al doped ZnO type CEMs and get no records.
standalone_edit = (W('point') + R('defects?'))
optimisation = W('carrier') + R('optimi[sz]')

from chemdataextractor.parse.cem import element_symbol
bcm = T('B-CM') | element_symbol
second_bcm = Optional((W('and') | Optional(W('along')).hide() + W('with')) + bcm)
in_place_of = bcm + W('in') + W('place') + W('of') + bcm

simple_cem_regex = R('(?:' + elements_or_string + '\d?)+')  # integer amounts of chemicals

# e.g. alloying with BaMg2Bi2
editing_leads = (editing_action + Optional(R('^with|of|by|via$')) + doping_percentages + simple_cem_regex + second_bcm).add_action(join)
# e.g. CO2 inclusions
editing_follows = (doping_percentages + simple_cem_regex + second_bcm + Optional(T('HYPH')) + editing_action + second_bcm).add_action(join)

editing_expression =  (editing_follows | editing_leads | standalone_edit | in_place_of).add_action(join)
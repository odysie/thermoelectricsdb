from chemdataextractor.parse import Optional, R, I, T, W, SkipTo
from chemdataextractor.parse.actions import join

#added optional hyphen
single_temp_or_pressure = ((R('high|low') + Optional(T('HYPH')) + R('temperature|pressure')) | R('^[HL][TP](?:[HL][TP])?$'))
qualitative_temp_or_pressure = single_temp_or_pressure + Optional(Optional(W('and')) + single_temp_or_pressure)

simple_processing = (Optional(R('ball|hot|cold|melt|arc|spark|mechanical|drop|vapour|laser|3D|powder|acid|screen')) + Optional(T('HYPH')) +
                         Optional(R('plasma')) + Optional(T('HYPH')) +
                         R('sinter|mill|drill|deposit|anneal|alloy|press|spun|spin|deform|process|fabri|cast|forg|roll|weld|extru|clad|print|mold|treat'))

processing_abbreviation = R('^(?:SPS|L?P?CVD|SILAR|P?LD)$') + Optional(Optional(T('HYPH')) + R('press'))

at_temperature_or_pressure = R('at') + T('CD') + (W('°C') | (Optional(R('°')) + R('[GkK]Pa(?:scals)?|k?bar|°?(((K|k)elvin(s)?)|K)\.?|(°C|((C|c)elsius))\.??')))  #sometimes '°C' is split sometimes not (?)

#just qualitative
#or processing, with optional temperature or pressure
#or just at a ceratin pressure
# v5 switched abbreviation and simple order
processing_expression = (qualitative_temp_or_pressure | ((processing_abbreviation | simple_processing) + Optional(at_temperature_or_pressure)) |
                         (R('at') + T('CD') + R('[GkK]Pa(?:scals)?|k?bar'))).add_action(join)

axes = (R('[xyzabc][xyzabc]?') + Optional(T('HYPH')) + R('axis|direction') | R('[xyzabc][xyzabc]?.?(?:ax[ie]s|directions?)') | (R('[xyzabc]') + R('^and$') + R('[xyzabc]') + R('axes|directions')))
crystallographic_direction = R('[\[\(][01][01][01][\)\]]') + R('direction|plane')
planes = R('in|out') + Optional(T('HYPH')) + Optional(R('of') + Optional(T('HYPH'))) + R('plane')
relative_to_process = R('perpendicular|parallel') + W('to') + W('the') + Optional(W('direction') + W('of')) + (processing_abbreviation | simple_processing)

direction_expression = (axes | planes | crystallographic_direction | relative_to_process).add_action(join)

contextual_label_expression = ( R('x|y') + R('^[=><≥≤]$') + T('CD') ).add_action(join)

ce = R('[A-Z][a-z]*\d*|\([^)]+\)\d*')
# only for verbs or nouns, no adjectives!
editing_action = R('substitut|incorporat|introduct?|dop(?:ing|ion)')  # NB: this has to be such that it doesn't start tagging 'doped' or else we lose Al doped ZnO type CEMs and get no records.
standalone_edit = (W('point') + R('defects?'))
optimisation = W('carrier') + R('optimi[sz]')

from chemdataextractor.parse.cem import element_symbol
bcm = T('B-CM')  |  element_symbol
# maybe I overdid it with this one?
second_bcm = Optional((W('and') | Optional(W('along')).hide() + W('with')) + bcm)
in_place_of = bcm + W('in') + W('place') + W('of') + bcm

# working examples:
# s = '{ peak ZT at 773 K }:  introducing 2D-MoSe2 into SnSe matrix achieved a high n of ∼2 × 1019 cm−3 without distinctly deteriorating κ'
# s = 'Effectively enhanced ZT value to 0.61 at 673 K has achieved in Cu1.8S by Bi3+ doping that is mainly attributed to an improved σ and a reduced κ'
# s = 'Pei and co-workers further optimized the carrier concentration of the Sb-doped GeTe sample by Se substitution and obtained a reasonably high zT of ∼1.95 at 725 K'

# add percentages
editing_expression = ((bcm + second_bcm + Optional(T('HYPH')) + editing_action + second_bcm) | (editing_action + Optional(R('^with|of|by|via$')) + bcm + second_bcm) | standalone_edit | in_place_of).add_action(join)  # is the optional joining word too permissive? should it be mandatory?

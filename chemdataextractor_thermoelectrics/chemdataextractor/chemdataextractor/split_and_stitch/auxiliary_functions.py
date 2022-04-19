# -*- coding: utf-8 -*-
"""
Auxiliary functions and classes for data extraction from the thermoelectric materials domain.

"""

from chemdataextractor.model import Compound, ModelType, StringType
from chemdataextractor.parse.auto import *
from chemdataextractor.doc.text import Sentence
from chemdataextractor import Document
from chemdataextractor.doc import Paragraph

import re
from pprint import pprint
from chemdataextractor.model.units.thermal_conductivity import ThermalConductivityModel
from chemdataextractor.model.units.power_factor import PowerFactorModel
from chemdataextractor.model.units.thermoelectric_models import ThermCond, PF
from chemdataextractor.model import DimensionlessModel
from chemdataextractor.parse.expressions_for_models import processing_expression, thermal_specifier_expression, pf_specifier_expression


# MASKING

element_names_regex = r'[Aa]ctinium|[Aa]luminium|[Aa]luminum|[Aa]mericium|[Aa]ntimony|[Aa]rgon|[Aa]rsenic|[Aa]statine|[Bb]arium|[Bb]erkelium|[Bb]eryllium|[Bb]ismuth|[Bb]ohrium|[Bb]oron|[Bb]romine|[Cc]admium|[Cc]aesium|[Cc]alcium|[Cc]alifornium|[Cc]arbon|[Cc]erium|[Cc]esium|[Cc]hlorine|[Cc]hromium|[Cc]obalt|[Cc]opernicium|[Cc]opper|[Cc]urium|[Dd]armstadtium|[Dd]ubnium|[Dd]ysprosium|[Ee]insteinium|[Ee]rbium|[Ee]uropium|[Ff]ermium|[Ff]lerovium|[Ff]luorine|[Ff]rancium|[Gg]adolinium|[Gg]allium|[Gg]ermanium|[Hh]afnium|[Hh]assium|[Hh]elium|[Hh]olmium|[Hh]ydrargyrum|[Hh]ydrogen|[Ii]ndium|[Ii]odine|[Ii]ridium|[Ii]ron|[Kk]alium|[Kk]rypton|[Ll]anthanum|[Ll]aIrencium|[Ll]ithium|[Ll]ivermorium|[Ll]utetium|[Mm]agnesium|[Mm]anganese|[Mm]eitnerium|[Mm]endelevium|[Mm]ercury|[Mm]olybdenum|[Nn]atrium|[Nn]eodymium|[Nn]eon|[Nn]eptunium|[Nn]ickel|[Nn]iobium|[Nn]itrogen|[Nn]obelium|[Oo]smium|[Oo]xygen|[Pp]alladium|[Pp]hosphorus|[Pp]latinum|[Pp]lumbum|[Pp]lutonium|[Pp]olonium|[Pp]otassium|[Pp]raseodymium|[Pp]romethium|[Pp]rotactinium|[Rr]adium|[Rr]adon|[Rr]henium|[Rr]hodium|[Rr]oentgenium|[Rr]ubidium|[Rr]uthenium|[Rr]utherfordium|[Ss]amarium|[Ss]candium|[Ss]eaborgium|[Ss]elenium|[Ss]ilicon|[Ss]ilver|[Ss]odium|[Ss]tannum|[Ss]tibium|[Ss]trontium|[Ss]ulfur|[Tt]antalum|[Tt]echnetium|[Tt]ellurium|[Tt]erbium|[Tt]hallium|[Tt]horium|[Tt]hulium|Tin|[Tt]itanium|[Tt]ungsten|[Uu]nunoctium|[Uu]nunpentium|[Uu]nunseptium|[Uu]nuntrium|[Uu]ranium|[Vv]anadium|[II]olfram|[Xx]enon|[Yy]tterbium|[Yy]ttrium|[Zz]inc|[Zz]irconium'
# element symbols, followed by a space full stop, or comma, but NOT PRECEEDED BY % and NOT followed by doped with OR %. So can catch Al doped Zno, and ZnO doped with 3 % Na, and ZnO doped with Na
# python's regex negative look-behind requires fixed-width pattern, so I have 3 different ORs | which match different possibilitites of doped with \d(\d)(%)
element_symbols_regex = r'(?<!(?:doped with|ed with \d%| with \d\.\d%|...undoped))(?:[\s\.,]H[\s\.,]|[\s\.,]He[\s\.,]|[\s\.,]Li[\s\.,]|[\s\.,]Be[\s\.,]|[\s\.,]B[\s\.,]|[\s\.,]C[\s\.,]|[\s\.,]N[\s\.,]|[\s\.,]O[\s\.,]|[\s\.,]F[\s\.,]|[\s\.,]' \
                        r'Ne[\s\.,]|[\s\.,]Na[\s\.,]|[\s\.,]Mg[\s\.,]|[\s\.,]Al[\s\.,]|[\s\.,]Si[\s\.,]|[\s\.,]P[\s\.,]|[\s\.,]Cl[\s\.,]|[\s\.,]Ar[\s\.,]|[\s\.,]Ca[\s\.,]|[\s\.,]Sc[\s\.,]|' \
                        r'[\s\.,]Ti[\s\.,]|[\s\.,]Cr[\s\.,]|[\s\.,]Mn[\s\.,]|[\s\.,]Fe[\s\.,]|[\s\.,]Co[\s\.,]|[\s\.,]Ni[\s\.,]|[\s\.,]Cu[\s\.,]|[\s\.,]Zn[\s\.,]|[\s\.,]Ga' \
                        r'[\s\.,]|[\s\.,]Ge[\s\.,]|[\s\.,]As[\s\.,]|[\s\.,]Se[\s\.,]|[\s\.,]Br[\s\.,]|[\s\.,]Kr[\s\.,]|[\s\.,]Rb[\s\.,]|[\s\.,]Sr[\s\.,]|[\s\.,]Y[\s\.,]|[\s\.,]Zr[\s\.,]|' \
                        r'[\s\.,]Nb[\s\.,]|[\s\.,]Mo[\s\.,]|[\s\.,]Tc[\s\.,]|[\s\.,]Ru[\s\.,]|[\s\.,]Rh[\s\.,]|[\s\.,]Pd[\s\.,]|[\s\.,]Ag[\s\.,]|[\s\.,]Cd[\s\.,]|[\s\.,]In[\s\.,]|[\s\.,]' \
                        r'Sn[\s\.,]|[\s\.,]Sb[\s\.,]|[\s\.,]Te[\s\.,]|[\s\.,]I[\s\.,]|[\s\.,]Xe[\s\.,]|[\s\.,]Cs[\s\.,]|[\s\.,]Ba[\s\.,]|[\s\.,]La[\s\.,]|[\s\.,]Ce[\s\.,]|[\s\.,]Pr[\s\.,]|' \
                        r'[\s\.,]Nd[\s\.,]|[\s\.,]Pm[\s\.,]|[\s\.,]Sm[\s\.,]|[\s\.,]Eu[\s\.,]|[\s\.,]Gd[\s\.,]|[\s\.,]Tb[\s\.,]|[\s\.,]Dy[\s\.,]|[\s\.,]Ho[\s\.,]|[\s\.,]Er[\s\.,]|[\s\.,]Tm' \
                        r'[\s\.,]|[\s\.,]Yb[\s\.,]|[\s\.,]Lu[\s\.,]|[\s\.,]Hf[\s\.,]|[\s\.,]Ta[\s\.,]|[\s\.,]Re[\s\.,]|[\s\.,]Os[\s\.,]|[\s\.,]Ir[\s\.,]|[\s\.,]Pt[\s\.,]|[\s\.,]Au[\s\.,]|' \
                        r'[\s\.,]Hg[\s\.,]|[\s\.,]Tl[\s\.,]|[\s\.,]Pb[\s\.,]|[\s\.,]Bi[\s\.,]|[\s\.,]Po[\s\.,]|[\s\.,]At[\s\.,]|[\s\.,]Rn[\s\.,]|[\s\.,]Fr[\s\.,]|[\s\.,]Ra[\s\.,]|[\s\.,]Ac' \
                        r'[\s\.,]|[\s\.,]Th[\s\.,]|[\s\.,]Pa[\s\.,]|[\s\.,]U[\s\.,]|[\s\.,]Np[\s\.,]|[\s\.,]Pu[\s\.,]|[\s\.,]Am[\s\.,]|[\s\.,]Cm[\s\.,]|[\s\.,]Bk[\s\.,]|[\s\.,]Cf[\s\.,]|[\s\.,]' \
                        r'Es[\s\.,]|[\s\.,]Fm[\s\.,]|[\s\.,]Md[\s\.,]|[\s\.,]No[\s\.,]|[\s\.,]Lr[\s\.,]|[\s\.,]Rf[\s\.,]|[\s\.,]Db[\s\.,]|[\s\.,]Sg[\s\.,]|[\s\.,]Bh[\s\.,]|[\s\.,]Hs[\s\.,]|[\s\.,]' \
                        r'Mt[\s\.,]|[\s\.,]Ds[\s\.,]|[\s\.,]Rg[\s\.,]|[\s\.,]Cn[\s\.,]|[\s\.,]Nh[\s\.,]|[\s\.,]Fl[\s\.,]|[\s\.,]Mc[\s\.,]|[\s\.,]Lv[\s\.,]|[\s\.,]Ts[\s\.,]|[\s\.,]Og[\s\.,])(?!doped|oping)' #recent change, added (d)oping
# skip K (to avoid problems with pottasium). also SKIP S, W or else we ruin Seebeck, Th Cond, PF etc. Consider also skipping He, In, I etc.

hypernyms = r'oxides?|cobaltites?|perovskites?|tellurides?|halides?|ferrites?|silicates?|sulfides?|aluminate|halogens?'

names_regex = element_names_regex + '|' + hypernyms
symbols_regex = element_symbols_regex


def mask_pollutant_values_in_text(t, xval):
    return re.sub(xval, 'xx', t)


def mask_pollutant_values_in_sentence(sentence, xval):
    return Sentence(mask_pollutant_values_in_text(sentence.text, xval))


percentage_doping = r'(\d+\.?\d*)\s?(?:mol|vol|wt|at)?\.?%'


# makes the text intended for a regex rule optional
def optional(x):
    return '(?:' + x + ')?'


doping_elements = '(?:Ag|Au|Br|Cd|Cl|Cu|Fe|Gd|Ge|Hg|Mg|Pb|Nb|Pd|Pt|Ru|Sb|Sc|Si|Sn|Ti|Xe|Zn|Zr|B|Ga|P|Bi|Li|PSS|RE|I)'

# recent change: Needs improvement. Now its just for single elements, only for 'doped/doping with'
contextual_doping = r'dop(?:ed|ing) with' + ' ?' + optional(percentage_doping) + ' ?' + doping_elements + '[ \.]'
# contextual_doping = r'doped with Nb'

improvement_percentage = r'(?:improvement of (\d+\.?\d*)\s?(?:mol|vol|wt|at)?\.?%)|(?:(\d+\.?\d*)\s?(?:mol|wt|at)?\.?% (?:improvement|higher|lower))'
extracted_percentage_doping = '-'


def mask_percentage_doping(t):
    return re.sub(improvement_percentage, '## % change', t)


times_regex = '\d+\.?\d*(\stimes)'
factor_regex = '(?<!power\s)(?:factor\sof\s\d+\.?\d*)' # factor of, NOT PRECEEDED BY power!!!


def mask_multiples(t):
    t = re.sub(times_regex, 'X times', t)
    return re.sub(factor_regex, 'factor of X', t)


class X_ThermCond(ThermalConductivityModel):
    """Used to provisionally identify thermal conductivity records for masking"""
    # specifier required tag to False <<<
    specifier = StringType(parse_expression=thermal_specifier_expression, required=False, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    parsers = [AutoSentenceParser()]


class X_PowerFactor(PowerFactorModel):
    """Used to provisionally identify power factor records for masking"""
    # specifier required tag to False <<<
    specifier = StringType(parse_expression=pf_specifier_expression, required=False, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)

    parsers = [AutoSentenceParser()]


class M_Process(DimensionlessModel):
    """Used to extract and mask processes"""
    compound = ModelType(Compound, required=True, contextual=False, updatable=False)
    specifier = StringType(parse_expression=processing_expression, required=False, contextual=False)
    parsers = [AutoSentenceParser()]


# returns true if record has names and temperature (value or rt mention)
# Also check if length two, or if ends in +
# pass given_model.__name__ as model_name
# There was probably a better way to do this using chemdataextractor
def record_has_name_and_temperature(rec, model_name, tests=False):
    #check there is a name
    if tests: print(f'model name: {model_name}')
    try:
        names = rec[model_name]['compound']['Compound']['names']
        specifier = rec[model_name]['specifier']  # confused... this is important. do not delete. why?
        r_val = rec[model_name]['raw_value']  # delete with caution...

        if tests: print(f'names: {names}')
        first_name = names[0]
        #extra name-related checks for acceptance. Recent change, added another minus sign and check start as well (including X. No Xenon things)
        if ((len(first_name) < 3) or (bool(re.search(r'\+|-|−', first_name[-1]))) or (bool(re.search(r'\+|-|−|X', first_name[0])))): #e.g. Li, O2, H, La3+, -Li... etc. (escaped + via \+)
            # print(f"rejected {first_name}")
            if tests: print(1)
            return False
    except Exception:
        if tests: print(2)
        return False
    #check temp value or rt mention
    try:
        temp = rec[model_name]['temperature']['Temperature']['raw_value'] # delete with caution...
        if tests: print(3)
        return True
    except KeyError:
        try:
            temp = rec[model_name]['room_temperature'] # delete with caution...
            if tests: print(4)
            return True
        except KeyError:
            if tests: print(5)
            return False


# SPLITTING (referred to as breaking)

change_from_to_regex = '(?:increase|decrease|improve|reduce|enhance|fluctuate|supresse?|exceede?|change|varie|rise|rose|drop(?:pe)?)[sd]?' # + from + to, break on 'to'.
comparison_regex = 'compar(?:ed?|able|ative)\s(?:to|with)'  # capture to or with
different_regex = '(?:(?:high|bigg|larg|low|small|bett)er)|reduction'

# optionally triggers for parentheses with anything in between. Hopefully
different_than_regex = different_regex + '(?:\s\(.+\))?' + '\sthan'


def check_comparison(sent_text):
    """Check if there are any comparisons in the text"""
    if bool(re.search(comparison_regex, sent_text)):
        return re.findall(comparison_regex, sent_text)
    else:
        return []


def check_change_from_to(sent_text):
    """Check if there are any change-type occurances in the text"""
    if (bool(re.search(change_from_to_regex, sent_text)) and bool(re.search('from',sent_text)) and bool(re.search('to',sent_text))):
        return ' to ' # don't forget the spaces, to aovid breaking up things such as 'factor'
    else:
        return False


def check_different_than(sent_text):
    """Check if there are any different-type comparisons in the text"""
    if bool(re.search(different_than_regex, sent_text)):
        return ' than '
    else:
        vs = re.findall('(?:v\.?s\.?)|(?:over)', sent_text, re.I)
        if (bool(re.search(different_regex, sent_text) and vs)):
            return vs[0] # unlikely that there are more than one types of vs
        else:
            single_word_different = re.findall('surpass|outperform|exceed|match|equal|;', sent_text, re.I)  # works for supasses, outperforms, exceeds etc.
            if single_word_different:
                return single_word_different[0]
    return False


def recover_previous_missing_unit(sent_text, given_model, regex_base):
    """Attempt to recover implied units from sentence"""
    temp_recs = Document(Paragraph(sent_text), models=[given_model]).records.serialize()
    if temp_recs:
        temp_rec = temp_recs[0]

        if record_has_name_and_temperature(temp_rec, given_model.__name__):
            units = temp_rec[given_model.__name__]['raw_units']
            value = temp_rec[given_model.__name__]['raw_value'].replace('.', '\.')  # escape . to use in regex

            regex_pattern = regex_base + value + ')'  # capture value as well, in order to avoid problematic splits
            regex_result = re.findall(regex_pattern, sent_text)  # why on earth is there a '' result??

            if regex_result and len(regex_result) == 1:
                regex_result = regex_result[0]  # if all good, grab the first (and only) result

                # split ON value to ensure correct placement of split, rather than just on 'and', but add value back later
                split = sent_text.split(regex_result)

                # only for len 2 now, repeat later
                if len(split) == 2:
                    # add value back (via regex result) and recover units where they were missing
                    sent_text = split[0] + ' ' + units + regex_result + split[1]
                    # don't name this variable different to sent_text
                    return sent_text

    return sent_text


def recover_respectively_units(sent_text, given_model):
    """Attempt to recover implied units from respectively-type sentence"""
    new_sent = sent_text  #to also keep previous version for stopping condition

    if(bool(re.search('respectively', sent_text)) and bool(re.search('and', sent_text))):

        # test if implied units (preceeded by number, followed by some form of and, followed by specific extracted value)
        regex_base = '\d(,? and '  # capture group is the '(,) and value' part. Leave parenthesis open, it is closed within function, following value
        # if our extracted value is preceeded by a number (without unit) and an 'and', then add units

        while True:
            new_sent = recover_previous_missing_unit(new_sent, given_model, regex_base)

            if new_sent == sent_text:
                break
            sent_text = new_sent
            regex_base = '\d(, '  # after recovering implied units for 'and' variants, proceed to recovery for commas

    return new_sent


def breaking(sent_text):
    """The splitting part of the `split-and-stitch` procedure"""
    breaking_points = check_comparison(sent_text)
    if check_change_from_to(sent_text):
        breaking_points.append(check_change_from_to(sent_text))
    if check_different_than(sent_text):
        breaking_points.append(check_different_than(sent_text))

    if breaking_points:
        break_regex = ''
        for bp in breaking_points:
            break_regex += (bp + '|')
        break_regex = break_regex[:-1]
        return re.split(break_regex, sent_text)
    else:
        return [sent_text]


def get_temp_from_record(rec, model_name):
    try:
        temp = rec[model_name]['room_temperature']
        return temp
    except KeyError:
        try:
            temp = rec[model_name]['temperature']['Temperature']['raw_value']
            temp_units = rec[model_name]['temperature']['Temperature']['raw_units']
            return temp + ' ' + temp_units
        except (KeyError, TypeError):
            return False


# FIX SEEBECK UNITS
def fix_for_seebeck_text(text):

    return text.replace('VK-1', 'V/K').replace('VK−1','V/K').replace('V K-1','V/K').replace('V K−1','V/K').replace('W/mK', 'Wm-1K-1')


# this has been observed to have some unexpected errors, such as with
# d = Document(fix_for_seebeck(Paragraph(s)), models=[Seebeck])
def fix_for_seebeck(para):
    try:
        return Paragraph(fix_for_seebeck_text(para.text))
    except Exception as e:
        # print(e)
        return para


def fix_html_for_seebeck(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        s = f.read()
        # these are to allow utf-8 encoding
        s = s.replace('-','-').replace('−','-').replace('≤','<')
        # these are to fix seebeck in the html situation
        s = s.replace('VK<small><sup>-1</sup></small>','V/K').replace('V K<small><sup>-1</sup></small>','V/K')
        print(s)

    fix_path = html_path.split('.html')[0] + '-Seebeck-FIX.html'
    with open(fix_path, "w+") as f:
        # RSC uses a weird non-unicode (?) symbol instead of -, it uses -, which is a pain to encode / decode... and now i ignore it, so it goes away completely. ruining the powers?
        f.write(s.encode('ascii', 'ignore').decode('ascii'))

    return fix_path




# -*- coding: utf-8 -*-
"""
The data extraction architecture described in the thermoelectric materials project.

Provides function te_parse, which processes an article, extracts records, and returns a pandas' DataFrame,
based on the adaptations performed for the thermoelectric materials project, as well as a list
of the extracted records, without any specific structuring. The steps executed perform
fixes on the units for the Seebeck coefficient, masking of pollutant values for ZT (Thermal Conductivity and
Power Factor, multiples, etc.), attempts to recover any implied units in respectively-type sentences,
the 'split-and-stitch' procedure described in the associated paper, and other relevant steps.
NB this is expected to be faster, if we skip the panda's DataFrame and just save the records
in a list (which could then be loaded into a DataFrame if one wants, after data extraction is complete).

"""

from chemdataextractor.doc import Sentence

import re
import pandas as pd
from pprint import pprint
from chemdataextractor.parse.restrict_values import RestrictionAutoSentenceParser

from .to_database import add_record_to_database

from .auxiliary_functions import fix_for_seebeck
from .auxiliary_functions import mask_multiples, mask_pollutant_values_in_sentence
from .auxiliary_functions import mask_percentage_doping, recover_respectively_units
from .auxiliary_functions import X_ThermCond, X_PowerFactor, M_Process

from .auxiliary_functions import breaking
from .auxiliary_functions import record_has_name_and_temperature
from .auxiliary_functions import get_temp_from_record

def te_parse(d, df, records_holder, filename, title, given_model, verbose = False, printing_records = False):
    """Extracts property information from a given article according to passed model

    :param d: The input document from which to extract property information
    :type d: class: `chemdataextractor.doc.document.Document`
    :param df: The DataFrame which will hold the data in the predetermined structure used in this project
    :param records_holder: A list to hold the serialized records without any specific structuring
    :param filename: The file name of the input document, expected in the form article-<DOI with hyphens>.<extension>
    :param title: The title of the article as text
    :param given_model: The model for which to extract property information
    :type given_model: class: `chemdataextractor.model.units.quantity_model._QuantityModelMeta`
    :param verbose: Prints the workings of the function if set to True, defaults to False
    :param printing records: Prints the records (even without values) if set to True, defaults to False
    :return: The updated df DataFrame and records_holder list
    :rtype: class: `pandas.core.frame.DataFrame` and class: `list`
    """
    given_model_name = given_model.__name__

    # FIX SEEBECK UNITS
    for para in d.paragraphs:
        para_rec_count = 0
        #fix for Seebeck
        if given_model_name in ['Seebeck', 'ThermCond', 'ZT']:
            old_para_text = para.text
            para = fix_for_seebeck(para)
            if old_para_text != para.text:
                pass

        for sent in para.sentences:
            sent_rec_count = 0

            # NORMAL PARSING
            given_model.parsers = [RestrictionAutoSentenceParser()]

            # MASKING POLLUTANT VALUES FOR ZT
            # test if given model is ZT in order to make pollutants exclusions
            if given_model_name == 'ZT':
                x_models = [X_ThermCond, X_PowerFactor]
                xdoc = sent
                xdoc.models = x_models
                exclusion_recs = xdoc.records.serialize()

                if exclusion_recs:
                    xsent = sent
                    for x_name in (x.__name__ for x in x_models):
                        for xrec in exclusion_recs:
                            try:
                                xval = xrec[x_name]['raw_value']
                                # one last test to remove spaces added from raw_value add_action(merge) in quantity.py
                                if xval not in xsent.text:
                                    xval = xval.replace(" ","")
                                xsent = mask_pollutant_values_in_sentence(xsent, xval)
                            except Exception as e:
                                pass
                else:
                    xsent = sent
            else:
                xsent = sent

            # MASKING AND DOPING EXTRACTION HAPPENS ONLY IN SENTENCE AND COMMA LEVEL PARSING?
            xsent_text = xsent.text

            # mask comparisons
            xsent_text = mask_multiples(xsent_text)

            # PERCENTAGE DOPING HAPPENS IN COMMA SENTNCE AND THEN IN SENTENCE
            # COMPARISONS BREAKING PARSING, which flows into commas parsing
            contextual_specifier, contextual_temperature = '',''
            temp_recs = Sentence(xsent_text, models=[given_model]).records.serialize()
            if temp_recs and len(temp_recs) > 1:  # v added len check

                temp_rec =  [tr for tr in temp_recs if given_model_name in tr]
                # grab the first element if there are any elements, else remain empty (which results in a False in the next if statement)
                temp_rec = temp_rec[0] if temp_rec else temp_rec

                if record_has_name_and_temperature(temp_rec, given_model_name):
                    contextual_temperature = get_temp_from_record(temp_rec, given_model_name)
                    contextual_specifier = temp_rec[given_model_name]['specifier']

                    # try and recover implied units in respectively-type sentences
                    if given_model_name != 'ZT':
                        xsent_text = recover_respectively_units(xsent_text, given_model)

                    breaking_sentences = breaking(xsent_text)

                    for break_index, break_sent in enumerate(breaking_sentences):
                        # just for testing
                        contextual_break_sent = '{' + contextual_specifier + ' at ' + contextual_temperature + '}: ' + break_sent

                        if verbose: print(f'break part #{break_index + 1} : {break_sent}')
                        # COMMA PARSING

                        # to backrun on break part with commas as well, if no comma records found
                        break_rec_count = 0  # don't forget to increment this
                        comma_sentences = break_sent.split(',')

                        # if there are comma breaks, also add the full break sentence at the end as an optional backrun
                        if len(comma_sentences) > 1:
                            comma_sentences_with_optional_break_sentence = comma_sentences + [break_sent]
                        else:
                            comma_sentences_with_optional_break_sentence = comma_sentences

                        # loop through the list using index, in order to check whether to rerun on break part
                        for i in range(len(comma_sentences_with_optional_break_sentence)):
                            level_note = 'comma-level'  # to inform on the level of extraction
                            # if it's the last entry, i.e. the break part without comma splitting
                            if (i + 1) == len(comma_sentences_with_optional_break_sentence):
                                # and if there are no records for that break so far
                                if break_rec_count == 0:
                                    # distinguish between no commas, or commas without records
                                    if verbose:
                                        if len(comma_sentences_with_optional_break_sentence) == 1:
                                            print("Running on full break part, since there aren't any commas.")
                                            level_note = 'break-part'
                                        else:
                                            print("Backrunning on break part, since no comma records were found!")
                                            level_note = 'break-part-backrun'
                                    # comma sent is set to be the last entry, i.e. the break part
                                    comma_sent = comma_sentences_with_optional_break_sentence[i]
                                else:
                                    if verbose: print("Does not run on break part, because comma records were found")
                                    continue
                            else:
                                comma_sent = comma_sentences_with_optional_break_sentence[i]

                            # extract (return 0) and mask (return 2) percentage doping
                            comma_sent = mask_percentage_doping(comma_sent)
                            # add contextual addition in squigly brackets, if it does not exist
                            # check for adding only specifier (if there is indication of extra temperature) or adding the temperature as well
                            contextual_addition = ''
                            if contextual_specifier not in comma_sent:
                                contextual_addition += contextual_specifier

                            temp_checks = '(?:\s[aA]t\s|\s[Nn]ear\s|\s[Aa]bove\s|\s[Aa]round\s)(?!the same temperature)'
                            if not bool(re.search(temp_checks, comma_sent)):
                                # print("no temp specifier found")
                                contextual_addition = contextual_addition + ' at ' + contextual_temperature

                            # if specifier or temperature needs to be added
                            if contextual_addition:
                                # needs the whitespace after { and before }!
                                contextual_comma_sent = '{ ' + contextual_addition + ' }: ' + comma_sent
                            else:
                                contextual_comma_sent = comma_sent


                            # SCAN FOR PROCESS. IF INCLUDES TEMPERATURE, MASK and add later to records
                            m_process = ''
                            try:
                                m_process_model = M_Process
                                m_process_records = Sentence(contextual_comma_sent, models=[m_process_model]).records.serialize()  # v changed to 1, as above
                                m_process = [mr for mr in m_process_records if m_process_model.__name__ in mr][0][m_process_model.__name__]['specifier']
                                # only go through with masking and adding if temperature value is inlcuded
                                if not (' K' in m_process or '°C' in m_process):  #what about ' KPa' for pressure?
                                    m_process = ''
                            except Exception as e:
                                if verbose: print(f"Error during process extraction for masking: {e}")
                                pass

                            if m_process:
                                contextual_comma_sent = re.sub(m_process, '*process*', contextual_comma_sent)

                            # comma doc
                            if verbose: print(f'contextual comma sent: {contextual_comma_sent}')

                            comma_recs = Sentence(contextual_comma_sent, models=[given_model]).records.serialize()
                            if comma_recs:
                                for comma_rec in comma_recs:
                                    if record_has_name_and_temperature(comma_rec, given_model_name):
                                        # ifextracted, add the m_process back in the record (very roundabout way)
                                        if m_process:  # m_process is valid only if there is a temperature value.
                                            comma_rec[given_model_name]['process'] = m_process


                                        if printing_records: pprint(comma_rec)
                                        if printing_records: print(('^' * 15))
                                        para_rec_count += 1
                                        sent_rec_count += 1
                                        break_rec_count += 1
                                        excerpt_from = '(' + contextual_comma_sent + ') FROM: ' + xsent_text

                                        df = add_record_to_database(comma_rec, df, filename, title, parser=level_note, excerpt=excerpt_from)
                                        records_holder.append(comma_rec)

            # If no records were found in sentences. (if sentence didn't have any commas then this doesn't trigger, but the comma sentence above is enough)
            # this means that we don't rerun on sentences which have breaking points but return no records, because those sentences tend to
            # be problematic if considered in their entirety
            if sent_rec_count == 0 and len(breaking(xsent_text)) == 1:
                # extract (return 0) and mask (retrun 2) percentage doping
                xsent_text = mask_percentage_doping(xsent_text)
                # use document derived from sentence, instead of sentence directly, because sentence returns records greedily (?)
                recs = Sentence(xsent_text, models=[given_model]).records.serialize()

                if recs:
                    for rec in recs:
                        if record_has_name_and_temperature(rec, given_model_name):

                            if verbose: print("Unbroken sentence:")
                            if printing_records: pprint(rec)
                            df = add_record_to_database(rec, df, filename, title, parser='unbroken sentence', excerpt=sent.text)
                            records_holder.append(rec)
                            para_rec_count += 1
                            if printing_records: print('-' * 15)



    return df, records_holder


#df template
df1 = pd.DataFrame(columns=['compound name', 'labels', 'doping', 'synthesis', 'confidence', 'model', 'specifier',
                            'value', 'units', 'temp_value', 'temp_units', 'room_temperature','filename'])

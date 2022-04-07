from pprint import pprint
from chemdataextractor import Document
from chemdataextractor.doc import Paragraph, Sentence
from chemdataextractor.relex import Snowball

import re
import pickle
import pandas as pd
from pprint import pprint
from chemdataextractor.parse.restrict_values import MyAutoSentenceParser

from to_database import add_record_to_database_extended_new, fix_for_seebeck
from new_functions import mask_multiples, mask_pollutant_values_in_sentence, mask_pollutant_values_in_text, mask_symbols_and_hypernyms_in_sentence, mask_symbols_and_hypernyms_in_text
from new_functions import extract_and_mask_percentage_doping, recover_respectively_units
from new_functions import X_ThermCond, X_PowerFactor, M_Process

from new_functions import breaking
from new_functions import get_temp_from_record
from new_functions import record_has_name_and_temperature

from new_functions import room_temp_regex, record_has_name_and_specifier, get_temp_from_record, drop_bad_temperature, has_temperature
from chemdataextractor.parse.models_for_TDE import Temperature_for_table_captions

#SNOWBALL SETUP for optional snowball_activation in new_parse
trigger_words = r'increas|decreas|reduce|higher|lower|respective|compar|both|improve|enhance|and' #removed 'and' for training

def amend_confidence(model_name):
    '''
    change the pattern's confidence in trained snowball model to 1.0
    '''

    path = '/Users/apple/Desktop/SC/THESIS/py_tests/chemdataextractor/relex/data/'

    #try first locally (Mac) and if not found check in cooley /home/oddy/
    try:
        with open((path + model_name + '.pkl'), 'rb') as f:
            snowball = pickle.load(f)
    except Exception as e:
        print("couldn't find snowball pkl locally, trying on cooley")
        print(e)

        path = '/home/oddy/'
        with open((path + model_name + '.pkl'), 'rb') as f:
            snowball = pickle.load(f)

    #get sum before
    print('\nGetting confidence sums...')
    s = 0.0
    for c in snowball.clusters:
        s += (c.pattern.confidence)
    print(f'before change: {s}')

    #amend
    for c in snowball.clusters:
        c.pattern.confidence = 1.0

    #get sum after
    s = 0.0
    for c in snowball.clusters:
        s += (c.pattern.confidence)
    print(f'after change: {s}\n')

    with open((path + model_name + '.pkl'), 'wb') as f:
        pickle.dump(snowball, f)

    return


my_save_name = 'trigger_ZT_TEST'

#let's just uncomment the ammending for mpi's sake for now
#amend_confidence(my_save_name)

#try locally then on Cooley
try:
    sb = Snowball.load(('/Users/apple/Desktop/SC/THESIS/py_tests/chemdataextractor/relex/data/' +my_save_name +'.pkl'))
except Exception as e:
    print("couldn't find on Mac. Trying Cooley")
    # sb = Snowball.load(('/home/oddy/' +my_save_name +'.pkl'))

# v change: commented out sb because it is not used now
# sb.learning_rate = 0
# sb.tsim = 65
# sb.tc = 0

specifier_words = r'conductivity|resistivity|σ|ρ|ϱ'


def bubble_parse(d, df, doi, title, given_model, snowball_activation = False):
    article_rec_count = 0

    for para in d.paragraphs:
        para_rec_count = 0
        #fix for Seebeck
        if given_model.__name__ == 'Seebeck':
            old_para_text = para.text
            para = fix_for_seebeck(para)
            if old_para_text != para.text:
                print(old_para_text)
                print('-=>')
                print(para)
        # pprint(para)

        sent_list = para.sentences

        previous_index = -1 #set the previous index to be -1, as in before the start of the paragraph
        for sentence_index in range(len(sent_list)):
            sent = sent_list[sentence_index]
            sent_rec_count = 0

            #print(sent)
            """changed = preprocess_text(sent.text)
            original = sent.text
            if (changed != original): #see the changes
                print(changed)
                print(original)
                print()"""


            #SNOWBALL
            sbrecs = []
            #skip snowball now, for RAM requirements
            if snowball_activation: #defaults to False
                if bool(re.search(trigger_words, sent.text)):
                    #print(f'trying Snowball on: {sent.text}')
                    given_model.parsers = [sb]
                    sbdoc = Document(sent, models=[given_model])
                    sbrecs = sbdoc.records.serialize()

            #test like this rather than in the if loop, so that the else resorts to MASP, regardless of finding trigger
            if sbrecs != []:
                for sbrec in sbrecs:
                    if record_has_name_and_temperature(sbrec, given_model.__name__):
                        print("FOUND WITH SNOWBALL:")
                        print(sent)
                        pprint(sbrec)
                        print(('#'*15))
                        para_rec_count += 1
                        sent_rec_count += 1
                        df = add_record_to_database_extended_new(sbrec, df, doi, title, parser='snowball', exrept=sent.text)


            #NORMAL PARSING
            else:
                if bool(re.search(specifier_words, sent.text)):
                    record_found = False
                    for depth in range(5):
                        if ((sentence_index - depth) > previous_index) and (not record_found):
                            slice = sent_list[sentence_index - depth: sentence_index + 1]
                            bubble = ''
                            for s in slice:
                                bubble += (s.text[:-1] + ' ') #remove the fullstop? Why do I have to? I was pretty certain ASP didn't care and would go beyond fullstops
                                #IR is different than just ignoring fullstops. What are the details though?

                            #print(f"bubble of depth {depth}: {bubble}")
                            #print()
                            sent = Sentence(bubble) #not sure if I should use Sentence, but we'll see

                            given_model.parsers = [MyAutoSentenceParser()]

                            #MASKING POLLUTANT VALUES FOR ZT
                            #test if given model is ZT in order to make pollutants exclusions
                            if (given_model.__name__ == 'ZT'):
                                xdoc = Document(sent, models=[X_ThermCond])
                                exclusion_recs = xdoc.records.serialize()
                                # pprint(exclusion_recs)
                                if exclusion_recs != []:
                                    # pprint(exclusion_recs)
                                    for xrec in exclusion_recs:
                                        try:
                                            # find a good way to access the names of models modularly
                                            xval = xrec['X_ThermCond']['raw_value']
                                            # print(xval)
                                            # print(f'original sentence: {sent}')
                                            xsent = mask_pollutant_values_in_sentence(sent, xval)
                                            # print(f'post-exclusion sentnence: {xsent}')
                                        except:
                                            print("coulnd't remove xval")
                                            xsent = sent
                                else:
                                    xsent = sent
                            else:
                                xsent = sent

                                # print(xval)
                                # remove values flagged for exception

                            #MASKING AND DOPING EXTRACTION HAPPENS ONLY IN SENTENCE AND COMMA LEVEL PARSING?
                            #MORE MASKING. Gotta work a bit between masking on text and masking on sentences
                            xsent_text = xsent.text
                            #mask comparisons
                            xsent_text = mask_multiples(xsent_text)

                            #PERCENTAGE DOPING HAPPENS IN COMMA SENTNCE AND THEN IN SENTENCE

                            #mask single element symbols and undesired hypernyms
                            xsent_text = mask_symbols_and_hypernyms_in_text(xsent_text)

                            #print(f"xsent_text: {xsent_text}")
                            #print('-')

                            #COMPARISONS BREAKING PARSING, which flows into commas parsing
                            contextual_specifier, contextual_temperature = '',''
                            #this temp stands for temporary, not temperature
                            temp_recs = Document(Paragraph(xsent_text), models=[given_model]).records.serialize()
                            if temp_recs:
                                temp_rec = temp_recs[0]
                                #pprint(temp_rec)
                                if record_has_name_and_temperature(temp_rec, given_model.__name__):
                                    #pprint(temp_rec)

                                    contextual_temperature = get_temp_from_record(temp_rec, given_model.__name__)
                                    contextual_specifier = temp_rec[given_model.__name__]['specifier']
                                    #print((contextual_specifier, contextual_temperature))


                                    for break_sent in breaking(xsent_text):
                                        #just tests
                                        contextual_break_sent = '{' + contextual_specifier + ' at ' + contextual_temperature + '}: ' + break_sent

                                        #print(f'original break sentence: {break_sent}')
                                        #print(f'contextual break sentence: {contextual_break_sent}')
                                        #stop here
                                        #COMMA PARSING
                                        for comma_sent in break_sent.split(','):
                                            # extract (return 0) and mask (retrun 2) percentage doping
                                            # v4 changed this, now it doesn't mask editing anymore (since SCEMs are not accepted as valid names)
                                            extracted_percentage_doping, comma_sent = extract_and_mask_percentage_doping(comma_sent)
                                            #add contextual addition in squigly brackets, if it does not exist
                                            #check for adding only specifier (if there is indication of extra temperature) or adding the temperature as well
                                            contextual_addition = ''
                                            if contextual_specifier not in comma_sent:
                                                contextual_addition += contextual_specifier
                                            temp_checks = ' at | near | above' #this is golden. Can it be generalised to any nested model?
                                            if not bool(re.search(temp_checks,comma_sent)):
                                                contextual_addition = contextual_addition + ' at ' + contextual_temperature

                                            #if specifier or temperature needs to be added
                                            if contextual_addition:
                                                contextual_comma_sent = '{ ' + contextual_addition + ' }: ' + comma_sent #needs the whitespace after { and before }!
                                            else:
                                                contextual_comma_sent = comma_sent

                                            #comma doc
                                            #print(f'contextual comma sent: {contextual_comma_sent}')
                                            comma_doc = Document(Paragraph(contextual_comma_sent), models=[given_model])
                                            comma_recs = comma_doc.records.serialize()
                                            if comma_recs != []:
                                                for comma_rec in comma_recs:
                                                    if record_has_name_and_temperature(comma_rec, given_model.__name__):
                                                        print(f'contextual comma sent at depth {depth}: {contextual_comma_sent}')
                                                        if extracted_percentage_doping:
                                                            print(f'extracted doping percentage: {extracted_percentage_doping}')
                                                        else:
                                                            extracted_percentage_doping = '-'
                                                        pprint(comma_rec)
                                                        print(('^' * 15))
                                                        para_rec_count += 1
                                                        sent_rec_count += 1

                                                        #if they are different
                                                        #have both the broken and full sentence in the excerpt in order to make sure we get the right thing during evaluation
                                                        if contextual_comma_sent != xsent_text:
                                                            excerpt_from = '(' + contextual_comma_sent + ') FROM: ' + xsent_text
                                                        else:
                                                            excerpt_from = xsent_text

                                                        df = add_record_to_database_extended_new(comma_rec, df, doi, title, parser='comma-level',
                                                                                                 exrept=excerpt_from, extracted_doping=extracted_percentage_doping, depth=depth)

                                                        #this is for bubble parsing
                                                        #print(excerpt_from)
                                                        previous_index = sentence_index #to make sure we don't look back enough as to catch previous records?
                                                        record_found = True

                            #If no records were found in sentences. (if sentence didn't have any commas then this doesn't trigger, but the comma sentence above is enough)
                            if sent_rec_count == 0:
                                # extract (return 0) and mask (retrun 2) percentage doping
                                extracted_percentage_doping, xsent_text = extract_and_mask_percentage_doping(xsent_text)
                                # use document derived from sentence, instead of sentence directly, because sentence returns records greedily (?)
                                prpdoc = Document(Paragraph(xsent_text), models=[given_model])
                                recs = prpdoc.records.serialize()

                                if recs != []:
                                    # print(sent.text + ':')
                                    # pprint(recs)
                                    # para_rec_count += len(recs) #this applies when pprinting all recs together rather than looping over them (and checking if they have temperature)
                                    # print('-'*15)

                                    for rec in recs:
                                        if record_has_name_and_temperature(rec, given_model.__name__):
                                            print(f'normal xsent at depth {depth}: {xsent_text}')
                                            if extracted_percentage_doping:
                                                print(f'extracted doping percentage: {extracted_percentage_doping}')
                                            else:
                                                extracted_percentage_doping = '-'
                                            pprint(rec)
                                            df = add_record_to_database_extended_new(rec, df, doi, title, parser='sentence', exrept=sent.text,
                                                                                     extracted_doping=extracted_percentage_doping, depth=depth)
                                            para_rec_count += 1
                                            print('-' * 15)
                                            previous_index = sentence_index  # to make sure we don't look back enough as to catch previous records?
                                            record_found = True

        if False:
            #print("Didn't find any records sentence-wide. Trying paragraph.")

            #mask paragraph. What about percentage doping? <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            prp_paratext = mask_multiples(mask_symbols_and_hypernyms_in_text(para.text))
            # for some reason Document(para,...) doesn't work. Needs Document(Paragraph(para.text),...)
            dpara = Document(Paragraph(prp_paratext), models=[given_model])
            recs = dpara.records.serialize()

            if recs != []:
                for rec in recs:
                    if record_has_name_and_temperature(rec, given_model.__name__):
                        df = add_record_to_database_extended_new(rec, df, doi, title, parser='paragraph', exrept=para.text)
                        print('No records found in sentences, but found in full Paragraph:')
                        pprint(prp_paratext + ':') #use pprint because paragraphs are big
                        pprint((rec))
                        para_rec_count += 1
                        print('~' * 15 + '\n')

        article_rec_count += para_rec_count

    print(f'Article rec counts = {article_rec_count}')
    return df

#new_addition record holder
# V3 changes: removed SCEM masking (handled internally through cem.py), removed full sentence parsing if there were any word breaks, removed paragraph parsing
def new_parse(d, df, records_holder, doi, title, given_model, snowball_activation = False):

    article_rec_count = 0

    # FIX SEEBECK UNITS
    for para in d.paragraphs:
        para_rec_count = 0
        #fix for Seebeck
        # v5 added fixes for ThermCond as well (should also trigger for ZT, to work with X_ThermCond). Make more modular
        if given_model.__name__ in ['Seebeck', 'ThermCond', 'ZT']:
            old_para_text = para.text
            para = fix_for_seebeck(para)
            if old_para_text != para.text:
                pass
                # print(old_para_text)
                # print('-=>')
                # print(para)
        # pprint(para)

        for sent in para.sentences:
            sent_rec_count = 0

            #print(sent)
            """changed = preprocess_text(sent.text)
            original = sent.text
            if (changed != original): #see the changes
                print(changed)
                print(original)
                print()"""


            # SNOWBALL
            sbrecs = []
            #skip snowball now, for RAM requirements
            if snowball_activation: #defaults to False
                if bool(re.search(trigger_words, sent.text)):
                    #print(f'trying Snowball on: {sent.text}')
                    given_model.parsers = [sb]
                    sbdoc = Document(sent, models=[given_model])
                    sbrecs = sbdoc.records.serialize()

            #test like this rather than in the if loop, so that the else resorts to MASP, regardless of finding trigger
            if sbrecs != []:
                for sbrec in sbrecs:
                    if record_has_name_and_temperature(sbrec, given_model.__name__):
                        print("FOUND WITH SNOWBALL:")
                        print(sent)
                        pprint(sbrec)
                        print(('#'*15))
                        para_rec_count += 1
                        sent_rec_count += 1
                        df = add_record_to_database_extended_new(sbrec, df, doi, title, parser='snowball', exrept=sent.text)
                        records_holder.append(sbrec)


            # NORMAL PARSING
            else:
                given_model.parsers = [MyAutoSentenceParser()]

                # MASKING POLLUTANT VALUES FOR ZT
                #test if given model is ZT in order to make pollutants exclusions
                if (given_model.__name__ == 'ZT'):
                    # v4 added X_PowerFactor as well
                    x_models = [X_ThermCond, X_PowerFactor]
                    xdoc = Document(sent, models=x_models)
                    exclusion_recs = xdoc.records.serialize()
                    # print("exclusion recs:")
                    # pprint(exclusion_recs)
                    if exclusion_recs != []:
                        # pprint(exclusion_recs)
                        xsent = sent
                        for x_name in (x.__name__ for x in x_models):
                            # print(f"x_name: {x_name}")
                            for xrec in exclusion_recs:
                                try:
                                    xval = xrec[x_name]['raw_value']
                                    # v5 small change
                                    if xval not in xsent.text:  # one last test to remove spaces added from raw_value add_action(merge) in quantity.py which I don't want to alter further
                                        xval = xval.replace(" ","")
                                    # print(f"{xval}")
                                    # print(f'original sentence: {xsent}')
                                    xsent = mask_pollutant_values_in_sentence(xsent, xval)
                                    # print(f'post-exclusion sentnence: {xsent}')
                                except Exception as e:
                                    # print(f"coulnd't remove xval due tp {e}")
                                    pass
                    else:
                        xsent = sent
                else:
                    xsent = sent

                    # print(xval)
                    # remove values flagged for exception


                # MASKING AND DOPING EXTRACTION HAPPENS ONLY IN SENTENCE AND COMMA LEVEL PARSING?
                #MORE MASKING. Gotta work a bit between masking on text and masking on sentences
                xsent_text = xsent.text

                #mask comparisons
                xsent_text = mask_multiples(xsent_text)

                #PERCENTAGE DOPING HAPPENS IN COMMA SENTNCE AND THEN IN SENTENCE

                #mask single element symbols and undesired hypernyms
                ### MASK_SYMBOLS_AND_HYPERNYMS EDITED TO DO NOTHING, FOR V2 TESTs
                #xsent_text = mask_symbols_and_hypernyms_in_text(xsent_text)

                # print(xsent_text)
                # print('-')

                #COMPARISONS BREAKING PARSING, which flows into commas parsing
                contextual_specifier, contextual_temperature = '',''
                temp_recs = Document(Paragraph(xsent_text), models=[given_model]).records.serialize()
                if temp_recs:
                    temp_rec = temp_recs[0]
                    # pprint(temp_rec)
                    if record_has_name_and_temperature(temp_rec, given_model.__name__):
                        contextual_temperature = get_temp_from_record(temp_rec, given_model.__name__)
                        contextual_specifier = temp_rec[given_model.__name__]['specifier']
                        #print((contextual_specifier, contextual_temperature))

                        # V4 addition
                        # if not ZT, then
                        # RECOVER ANY POSSIBLE IMPLIED UNITS IN RESPECTIVELY TYPE SENTENCES
                        if given_model.__name__ != 'ZT':
                            xsent_text = recover_respectively_units(xsent_text, given_model)
                            # print(f"xsent following unit recovery: {xsent_text}")

                        for break_sent in breaking(xsent_text):
                            # just tests
                            contextual_break_sent = '{' + contextual_specifier + ' at ' + contextual_temperature + '}: ' + break_sent

                            # print(f'original break sentence: {break_sent}')
                            # print(f'contextual break sentence: {contextual_break_sent}')
                            # stop here
                            #COMMA PARSING
                            for comma_sent in break_sent.split(','):
                                # extract (return 0) and mask (retrun 2) percentage doping
                                extracted_percentage_doping, comma_sent = extract_and_mask_percentage_doping(comma_sent)
                                # add contextual addition in squigly brackets, if it does not exist
                                # check for adding only specifier (if there is indication of extra temperature) or adding the temperature as well
                                contextual_addition = ''
                                if contextual_specifier not in comma_sent:
                                    contextual_addition += contextual_specifier
                                # this is golden. Can it be generalised to any nested model using specifer expression?
                                # v4 change ' ' to '\s'. Apparently this wasn't working properly for some time now. How about at sentence start?
                                # v5 added negative lookahead to still add contextual temp for cases such as 'at the same temperature'
                                temp_checks = '(?:\s[aA]t\s|\s[Nn]ear\s|\s[Aa]bove\s|\s[Aa]round\s)(?!the same temperature)'
                                if not bool(re.search(temp_checks,comma_sent)):
                                    # print("no temp specifier found")
                                    contextual_addition = contextual_addition + ' at ' + contextual_temperature

                                # print(f"temp search results: {re.search(temp_checks,comma_sent)}")
                                # if specifier or temperature needs to be added
                                if contextual_addition:
                                    contextual_comma_sent = '{ ' + contextual_addition + ' }: ' + comma_sent  # needs the whitespace after { and before }!
                                else:
                                    contextual_comma_sent = comma_sent


                                # V4 SCAN FOR PROCESS. IF INCLUDES TEMPERATURE, MASK and add later to records
                                m_process = ''
                                try:
                                    m_process_model = M_Process
                                    m_process = Document(Paragraph(contextual_comma_sent), models=[m_process_model]).records.serialize()[0][m_process_model.__name__]['specifier']
                                    # only go through with masking and adding if temperature value is inlcuded
                                    if not (' K' in m_process or '°C' in m_process):  #what about ' KPa' for pressure?
                                        m_process = ''
                                    # print(m_process)
                                except Exception as e:
                                    # print(f"Error during process extraction for masking: {e}")
                                    pass

                                if m_process:
                                    contextual_comma_sent = re.sub(m_process, '*process*', contextual_comma_sent)

                                # comma doc
                                # print(f'contextual comma sent: {contextual_comma_sent}')

                                comma_doc = Document(Paragraph(contextual_comma_sent), models=[given_model])
                                comma_recs = comma_doc.records.serialize()
                                if comma_recs != []:
                                    for comma_rec in comma_recs:
                                        if record_has_name_and_temperature(comma_rec, given_model.__name__):
                                            #v4 if extracted, add the m_process back in the record (very roundabout way)
                                            if m_process:  # m_process is valid only if there is a temperature value.
                                                comma_rec[given_model.__name__]['process'] = m_process

                                            ##print(contextual_comma_sent)
                                            if extracted_percentage_doping:
                                                # print(f'extracted doping percentage: {extracted_percentage_doping}')
                                                pass
                                            else:
                                                extracted_percentage_doping = '-'
                                            #pprint(comma_rec)
                                            ##print(('^' * 15))
                                            para_rec_count += 1
                                            sent_rec_count += 1
                                            #have both the broken and full sentence in the excerpt in order to make sure we get the right thing during evaluation
                                            excerpt_from = '(' + contextual_comma_sent + ') FROM: ' + xsent_text

                                            df = add_record_to_database_extended_new(comma_rec, df, doi, title, parser='comma-level', exrept=excerpt_from, extracted_doping=extracted_percentage_doping)
                                            records_holder.append(comma_rec)

                # v5 try this functionality for unbroken sentences. If the FP are too high, then ditch it.
                # If no records were found in sentences. (if sentence didn't have any commas then this doesn't trigger, but the comma sentence above is enough)
                if sent_rec_count == 0 and len(breaking(xsent_text)) == 1:
                    # extract (return 0) and mask (retrun 2) percentage doping
                    extracted_percentage_doping, xsent_text = extract_and_mask_percentage_doping(xsent_text)
                    # use document derived from sentence, instead of sentence directly, because sentence returns records greedily (?)
                    prpdoc = Document(Paragraph(xsent_text), models=[given_model])
                    recs = prpdoc.records.serialize()

                    if recs != []:
                        # print(sent.text + ':')
                        # pprint(recs)
                        # para_rec_count += len(recs) #this applies when pprinting all recs together rather than looping over them (and checking if they have temperature)
                        # print('-'*15)

                        for rec in recs:
                            if record_has_name_and_temperature(rec, given_model.__name__):
                                ##print(xsent_text + ':\n')
                                if extracted_percentage_doping:
                                    # print(f'extracted doping percentage: {extracted_percentage_doping}')
                                    pass
                                else:
                                    extracted_percentage_doping = '-'
                                ##pprint(rec)
                                df = add_record_to_database_extended_new(rec, df, doi, title, parser='unbroken sentence', exrept=sent.text, extracted_doping=extracted_percentage_doping)
                                records_holder.append(rec)
                                para_rec_count += 1
                                print('-' * 15)

        # PARAGRAPH PARSE
        if False:  # para_rec_count == 0:
            #print("Didn't find any records sentence-wide. Trying paragraph.")

            #mask paragraph. What about percentage doping? <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            prp_paratext = mask_multiples(mask_symbols_and_hypernyms_in_text(para.text))
            # for some reason Document(para,...) doesn't work. Needs Document(Paragraph(para.text),...)
            dpara = Document(Paragraph(prp_paratext), models=[given_model])
            recs = dpara.records.serialize()

            if recs != []:
                for rec in recs:
                    if record_has_name_and_temperature(rec, given_model.__name__):
                        df = add_record_to_database_extended_new(rec, df, doi, title, parser='paragraph', exrept=para.text)
                        records_holder.append(rec)
                        print('No records found in sentences, but found in full Paragraph:')
                        pprint(prp_paratext + ':') #use pprint because paragraphs are big
                        pprint((rec))
                        para_rec_count += 1
                        print('~' * 15 + '\n')

        article_rec_count += para_rec_count

    print(f'Article rec counts = {article_rec_count}')
    return df, records_holder


#new_addition record holder
# V3 changes: removed SCEM masking (handled internally through cem.py), removed full sentence parsing if there were any word breaks, removed paragraph parsing
def v_parse(d, df, records_holder, doi, title, given_model, snowball_activation = False, verbose = False, printing_records = False):

    given_model_name = given_model.__name__
    article_rec_count = 0

    # FIX SEEBECK UNITS
    for para in d.paragraphs:
        para_rec_count = 0
        #fix for Seebeck
        # v5 added fixes for ThermCond as well (should also trigger for ZT, to work with X_ThermCond). Make more modular
        if given_model_name in ['Seebeck', 'ThermCond', 'ZT']:
            old_para_text = para.text
            para = fix_for_seebeck(para)
            if old_para_text != para.text:
                pass
                # print(old_para_text)
                # print('-=>')
                # print(para)
        # pprint(para)

        for sent in para.sentences:
            sent_rec_count = 0

            #print(sent)
            """changed = preprocess_text(sent.text)
            original = sent.text
            if (changed != original): #see the changes
                print(changed)
                print(original)
                print()"""


            # NORMAL PARSING
            given_model.parsers = [MyAutoSentenceParser()]

            # MASKING POLLUTANT VALUES FOR ZT
            #test if given model is ZT in order to make pollutants exclusions
            if (given_model_name == 'ZT'):
                # v4 added X_PowerFactor as well
                x_models = [X_ThermCond, X_PowerFactor]
                xdoc = sent
                xdoc.models = x_models  # missed in first massive v5 run...
                exclusion_recs = xdoc.records.serialize()
                # print("exclusion recs:")
                # pprint(exclusion_recs)
                if exclusion_recs != []:
                    xsent = sent
                    for x_name in (x.__name__ for x in x_models):
                        # print(f"x_name: {x_name}")
                        for xrec in exclusion_recs:
                            try:
                                xval = xrec[x_name]['raw_value']
                                # v5 small change
                                if xval not in xsent.text:  # one last test to remove spaces added from raw_value add_action(merge) in quantity.py which I don't want to alter further
                                    xval = xval.replace(" ","")
                                # print(f"{xval}")
                                # print(f'original sentence: {xsent}')
                                xsent = mask_pollutant_values_in_sentence(xsent, xval)
                                # print(f'post-exclusion sentnence: {xsent}')
                            except Exception as e:
                                # print(f"couldn't remove xval due to {e}")
                                pass
                else:
                    xsent = sent
            else:
                xsent = sent

                # print(xval)
                # remove values flagged for exception


            # MASKING AND DOPING EXTRACTION HAPPENS ONLY IN SENTENCE AND COMMA LEVEL PARSING?
            #MORE MASKING. Gotta work a bit between masking on text and masking on sentences
            xsent_text = xsent.text
            # print(f"xsent after pollutants masking: {xsent_text}")

            #mask comparisons
            xsent_text = mask_multiples(xsent_text)

            #PERCENTAGE DOPING HAPPENS IN COMMA SENTNCE AND THEN IN SENTENCE

            #mask single element symbols and undesired hypernyms
            ### MASK_SYMBOLS_AND_HYPERNYMS EDITED TO DO NOTHING, FOR V2 TESTs
            #xsent_text = mask_symbols_and_hypernyms_in_text(xsent_text)

            # print(xsent_text)
            # print('-')

            #COMPARISONS BREAKING PARSING, which flows into commas parsing
            contextual_specifier, contextual_temperature = '',''
            temp_recs = Sentence(xsent_text, models=[given_model]).records.serialize()
            if temp_recs and len(temp_recs) > 1:  # v added len check
                # print("all temporary recs")
                # pprint(temp_recs)
                temp_rec =  [tr for tr in temp_recs if given_model_name in tr]  # v fix to get the right record because Sentences also get Compound(s) or Temperature records individually.
                temp_rec = temp_rec[0] if temp_rec else temp_rec  # grab the first element if there are any elements, else remain empty (which results in a False in the next if statement)

                # print(xsent_text)
                # print("temporary rec:")
                # pprint(temp_rec)
                if record_has_name_and_temperature(temp_rec, given_model_name):
                    contextual_temperature = get_temp_from_record(temp_rec, given_model_name)
                    contextual_specifier = temp_rec[given_model_name]['specifier']
                    #print((contextual_specifier, contextual_temperature))

                    # V4 addition
                    # if not ZT, then
                    # RECOVER ANY POSSIBLE IMPLIED UNITS IN RESPECTIVELY TYPE SENTENCES
                    if given_model_name != 'ZT':
                        xsent_text = recover_respectively_units(xsent_text, given_model)
                        # print(f"xsent following unit recovery: {xsent_text}")

                    breaking_sentences = breaking(xsent_text)

                    for break_index, break_sent in enumerate(breaking_sentences):
                        # just tests
                        contextual_break_sent = '{' + contextual_specifier + ' at ' + contextual_temperature + '}: ' + break_sent

                        if verbose: print(f'break part #{break_index + 1} : {break_sent}')
                        # if printing: print(f'contextual break sentence: {contextual_break_sent}')
                        # stop here
                        #COMMA PARSING

                        # v8 THIS IS NEW, to backrun on break part with commas as well, if no comma records found
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
                                            level_note = 'break-part'  # this used to be considered comma-level
                                        else:
                                            print("Backrunning on break part, since no comma records were found!")
                                            level_note = 'break-part-backrun' # this is the v8 addition essentially
                                    # comma sent is set to be the last entry, i.e. the break part
                                    comma_sent = comma_sentences_with_optional_break_sentence[i]
                                else:
                                    if verbose: print("Does not run on break part, because comma records were found")
                                    continue
                            else:
                                comma_sent = comma_sentences_with_optional_break_sentence[i]

                            # v8 NB called comma_sent but may be the break part. Need better naming?

                            # extract (return 0) and mask (return 2) percentage doping
                            extracted_percentage_doping, comma_sent = extract_and_mask_percentage_doping(comma_sent)
                            # add contextual addition in squigly brackets, if it does not exist
                            # check for adding only specifier (if there is indication of extra temperature) or adding the temperature as well
                            contextual_addition = ''
                            if contextual_specifier not in comma_sent:
                                contextual_addition += contextual_specifier
                            # this is golden. Can it be generalised to any nested model using specifer expression?
                            # v4 change ' ' to '\s'. Apparently this wasn't working properly for some time now. How about at sentence start?
                            # v5 added negative lookahead to still add contextual temp for cases such as 'at the same temperature'
                            temp_checks = '(?:\s[aA]t\s|\s[Nn]ear\s|\s[Aa]bove\s|\s[Aa]round\s)(?!the same temperature)'
                            if not bool(re.search(temp_checks, comma_sent)):
                                # print("no temp specifier found")
                                contextual_addition = contextual_addition + ' at ' + contextual_temperature

                            # print(f"temp search results: {re.search(temp_checks,comma_sent)}")
                            # if specifier or temperature needs to be added
                            if contextual_addition:
                                contextual_comma_sent = '{ ' + contextual_addition + ' }: ' + comma_sent  # needs the whitespace after { and before }!
                            else:
                                contextual_comma_sent = comma_sent


                            # V4 SCAN FOR PROCESS. IF INCLUDES TEMPERATURE, MASK and add later to records
                            m_process = ''
                            try:
                                m_process_model = M_Process
                                m_process_records = Sentence(contextual_comma_sent, models=[m_process_model]).records.serialize()  # v changed to 1, as above
                                m_process = [mr for mr in m_process_records if m_process_model.__name__ in mr][0][m_process_model.__name__]['specifier']
                                # only go through with masking and adding if temperature value is inlcuded
                                if not (' K' in m_process or '°C' in m_process):  #what about ' KPa' for pressure?
                                    m_process = ''
                                # print(m_process)
                            except Exception as e:
                                # print(f"Error during process extraction for masking: {e}")
                                pass

                            if m_process:
                                contextual_comma_sent = re.sub(m_process, '*process*', contextual_comma_sent)

                            # comma doc
                            if verbose: print(f'contextual comma sent: {contextual_comma_sent}')

                            comma_recs = Sentence(contextual_comma_sent, models=[given_model]).records.serialize()
                            if comma_recs != []:
                                for comma_rec in comma_recs:
                                    if record_has_name_and_temperature(comma_rec, given_model_name):
                                        #v4 if extracted, add the m_process back in the record (very roundabout way)
                                        if m_process:  # m_process is valid only if there is a temperature value.
                                            comma_rec[given_model_name]['process'] = m_process

                                        ##print(contextual_comma_sent)
                                        if extracted_percentage_doping:
                                            # print(f'extracted doping percentage: {extracted_percentage_doping}')
                                            pass
                                        else:
                                            extracted_percentage_doping = '-'
                                        if printing_records: pprint(comma_rec)
                                        if printing_records: print(('^' * 15))
                                        para_rec_count += 1
                                        sent_rec_count += 1
                                        break_rec_count += 1
                                        #have both the broken and full sentence in the excerpt in order to make sure we get the right thing during evaluation
                                        excerpt_from = '(' + contextual_comma_sent + ') FROM: ' + xsent_text

                                        df = add_record_to_database_extended_new(comma_rec, df, doi, title, parser=level_note, exrept=excerpt_from, extracted_doping=extracted_percentage_doping)
                                        records_holder.append(comma_rec)

            # v5 try this functionality for unbroken sentences. If the FP are too high, then ditch it.
            # If no records were found in sentences. (if sentence didn't have any commas then this doesn't trigger, but the comma sentence above is enough)
            # this means that we don't rerun on sentences which have breaking points but return no records, because those sentences tend to
            # be problematic if considered in their entirety
            if sent_rec_count == 0 and len(breaking(xsent_text)) == 1:
                # extract (return 0) and mask (retrun 2) percentage doping
                extracted_percentage_doping, xsent_text = extract_and_mask_percentage_doping(xsent_text)
                # use document derived from sentence, instead of sentence directly, because sentence returns records greedily (?)
                recs = Sentence(xsent_text, models=[given_model]).records.serialize()

                if recs != []:
                    # print(sent.text + ':')
                    # pprint(recs)
                    # para_rec_count += len(recs) #this applies when pprinting all recs together rather than looping over them (and checking if they have temperature)
                    # print('-'*15)

                    for rec in recs:
                        if record_has_name_and_temperature(rec, given_model_name):
                            ##print(xsent_text + ':\n')
                            if extracted_percentage_doping:
                                # print(f'extracted doping percentage: {extracted_percentage_doping}')
                                pass
                            else:
                                extracted_percentage_doping = '-'
                            if verbose: print("Unbroken sentence:")
                            if printing_records: pprint(rec)
                            df = add_record_to_database_extended_new(rec, df, doi, title, parser='unbroken sentence', exrept=sent.text, extracted_doping=extracted_percentage_doping)
                            records_holder.append(rec)
                            para_rec_count += 1
                            if printing_records: print('-' * 15)


        article_rec_count += para_rec_count

    print(f'Article rec counts = {article_rec_count}')
    return df, records_holder




#df template
df1 = pd.DataFrame(columns=['compound name', 'labels', 'doping', 'synthesis', 'confidence', 'model', 'specifier', 'value', 'units', 'temp_value', 'temp_units', 'room_temperature','doi'])


#TDE

#yield records from tde parsing
def tde_parse(d, given_model):

    d.models = [given_model]

    t_count = 1
    for table in d.tables:
        #PRINT EVERY TABLE:
        #print(f'table {t_count}...')
        caption_temperature_recs, record = [], []  # these needs a reset every table for some reason

        if table.records:
            #PRINT ONLY TABLES WITH RECORDS:
            print('TABLE CAPTION:')
            print(table.caption)
            print('TABLE:')
            print(table.tde_table)

            table_caption_text = table.caption.text
            table_caption_doc = Document(Paragraph(table_caption_text), models=[Temperature_for_table_captions])
            caption_temperature_recs = table_caption_doc.records.serialize()
            print("Table Caption records:")
            pprint(caption_temperature_recs)

            # DIRECT EXTRACTION OF ROOM TEMPERATURE MENTION
            room_temp_extraction = re.findall(room_temp_regex, table_caption_text, re.I)
            #if room_temp_extraction:
                #check(room_temp_extraction, 'room temp extraction', CHECKS)

            model_name = given_model.__name__

            print(f'RECORDS from {model_name}:')
            for table_record in table.records:
                record = table_record.serialize()
                if record_has_name_and_specifier(record, model_name):

                    #check(record, 'record before additions', CHECKS)

                    # drop bad temperatures
                    record = drop_bad_temperature(record, model_name)

                    # after possible bad temperatures have been dropped
                    # check if there is a temperature in the record
                    # and if not, add possible temperature records from the caption
                    if caption_temperature_recs and not has_temperature(record, model_name):
                        record[model_name]['temperature'] = caption_temperature_recs[0]
                    if room_temp_extraction and not has_temperature(record, model_name):
                        record[model_name]['room_temperature'] = room_temp_extraction[0]
                        # unlikely that there is more than one such extraction
                    if record:  # this should be reduntant, but it's not
                        pprint(record)
                        #try the yielding and loop over to append to databases and json file
                        yield record
        t_count += 1



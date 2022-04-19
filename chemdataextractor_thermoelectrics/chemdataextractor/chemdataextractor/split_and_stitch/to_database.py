# -*- coding: utf-8 -*-
"""
Function to transform the records extracted via te_parse into a database.
"""
import logging


def add_record_to_database(record, df, filename, title, parser, excerpt ='-'):
    """Adds record to the DataFrame database, according to expected structure.

    :param record: The extracted record, serialized
    :type record: class: `dict`
    :param df: The DataFrame which will hold the data in the predetermined structure used in this project
    :param filename: The file name of the input document, expected in the form article-<DOI with hyphens>.<extension>
    :param title: The title of the article as text
    :param title: A text note on the parser or level of data extraction
    :param excerpt: The part of the text from which the data record was extracted
    :return: The updated df DataFrame
    :rtype: class: `pandas.core.frame.DataFrame`
    """

    # set everything clean
    compound, editing, temperature, compound_name, label, confidence, synthesis, editing, key, specifier, value, units,\
    temp_value, temp_units, room_temperature, pressure, pressure_value, pressure_units, process, direction_of_measurement, raw_units, raw_value,\
        error, contextual_label = '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',\
                                  '-', '-', '-', '-', '-', '-'

    for model_name in record:
        model = record[model_name]

        try:
            compound = model['compound']
        except KeyError:
            pass
            # logging.error(f"couldn't find compound in {model_name}")

        try:
            compound_name = compound['Compound']['names']
        except KeyError:
            pass
            # logging.error(f"couldn't find compound name in {model_name}")

        try:
            label = compound['Compound']['labels']
        except KeyError:
            pass
            # logging.error(f"couldn't find label in {model_name}")

        try:
            synthesis = model['synthesis']
        except KeyError:
            pass
            # logging.error(f"couldn't find synthesis in {model_name}")

        try:
            editing = model['editing']
        except KeyError:
            pass
            # logging.error(f"couldn't find editing in {model_name}")

        try:
            process = model['process']
        except KeyError:
            pass
            # logging.error(f"couldn't find confidence in {model_name}")
            
        try:
            direction_of_measurement = model['direction_of_measurement']
        except KeyError:
            pass
            # logging.error(f"couldn't find confidence in {model_name}")
            
        try:
            confidence = model['confidence']
        except KeyError:
            pass
            # logging.error(f"couldn't find confidence in {model_name}")

        try:
            specifier = model['specifier']
        except KeyError:
            pass
            # logging.error(f"couldn't find specifier in {model_name}")

        try:
            value = model['value']  # instead of raw value
        except KeyError:
            pass
            # logging.error(f"couldn't find value in {model_name}")

        try:
            units = model['units']  # instead of raw units
        except KeyError:
            pass
            # logging.error(f"couldn't find units in {model_name}")
    
        try:
            raw_value = model['raw_value'] 
        except KeyError:
            pass
            # logging.error(f"couldn't find raw_value in {model_name}")

        try:
            raw_units = model['raw_units']
        except KeyError:
            pass
            # logging.error(f"couldn't find units in {model_name}")
            
        try:
            error = model['error'] 
        except KeyError:
            pass
            # logging.error(f"couldn't find error in {model_name}")

        try:
            contextual_label = model['contextual_label'] 
        except KeyError:
            pass
            # logging.error(f"couldn't find contextual_label in {model_name}")
            
        try:
            room_temperature = model['room_temperature']
        except KeyError:
            pass
            # logging.debug('no room temperature mention')

        # NESTED TEMPERATURE MODEL, OR ADDED TEMPERATURE FROM TABLE's CAPTION
        try:
            temperature = model['temperature']['Temperature']
        except:
            try:
                temperature = model['temperature']['Temperature_for_table_captions']
            except KeyError:
                pass
                # logging.error(f"couldn't find temperature model in {model_name}")

        if temperature:
            try:
                temp_value = temperature['value'] # not raw
            except KeyError:
                pass
                # logging.error(f"couldn't find temperature value in {model_name}")

            try:
                temp_units = temperature['units'] # not raw
            except KeyError:
                pass
                # logging.error(f"couldn't find temperature unit in {model_name}")

        # NESTED PRESSURE MODEL
        try:
            pressure = model['pressure']['Pressure']
        except KeyError:
            pass
            # logging.error(f"couldn't find pressure model in {model_name}")

        if pressure:
            try:
                pressure_value = pressure['value']  # not raw
            except KeyError:
                pass
                # logging.error(f"couldn't find pressure value in {model_name}")

            try:
                pressure_units = pressure['units']  # not raw
            except KeyError:
                pass
                # logging.error(f"couldn't find pressure unit in {model_name}")

    dictionary = {'compound_name': compound_name, 'labels': label, 'editing': editing,
                  'model': model_name, 'specifier': specifier, 'raw_units': raw_units, 'raw_value': raw_value, 'error': error,
                  'value': value, 'units': units, 'temp_value': temp_value, 'temp_units': temp_units, 'room_temperature': room_temperature,
                  'process': process, 'direction_of_measurement': direction_of_measurement, 'excerpt': excerpt, 'filename': filename,
                  'title': title, 'parser' : parser, 'pressure_value': pressure_value, 'pressure_units':pressure_units}

    df = df.append(dictionary, ignore_index=True)
    return df

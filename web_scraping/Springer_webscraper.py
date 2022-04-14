import os
import sys
import requests
import pickle
from pprint import pprint
import urllib.request
import joblib
import re
# from chemdataextractor2.doc import Sentence, Document, Paragraph
from tabledataextractor import Table
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from pprint import pprint


def search_tdmapi(s, p, empty, dump_temp):

    '''
    search Springer articles using the TDM API

    output: raw response in JATS format

    inputs:
        s(int): returned articles start from this number
        p(int): the number of articles in a single query (maximum = 50)
        empty(string): "contain" constraints for the search
        dump_temp(boolean): whether or not to save the raw response to xml files
    '''

    base_url = 'https://articles-api.springer.com/xmldata/jats'
    spr_url = '{}?q={}&excludeElements=Bibliography&api_key={}&s={}&p={}'.format(base_url, empty, tdm_api_key, s, p)
    sav_name = '{}_s={}_p={}.xml'.format(empty, s, p).replace(':', "=").replace('%22', "").replace('%20', "_")

    response = requests.get(spr_url)
    
    if response:
        total, start, displayed, query = get_total(response.text)
        # print('search success, total = {}, start = {}, displayed = {}, query = {}'.format(total, start, displayed, query), '\n')
        if dump_temp == True:
            with open(sav_name, 'w', encoding='utf-8') as f:
                f.write(response.text)
    else:
        print('search error', response)
        sys.exit()

    return response.text


def get_total(raw_text):

    '''
    find the summary of the query results
    sub-function

    output(int): the number of articles

    inputs:
        raw_text(string): text from the response
    '''

    patterns = {
        'result': [r'<result>', r'</result>'],
        'total': [r'<total>', r'</total>'],
        'start': [r'<start>', r'</start>'],
        'displayed': [r'<recordsDisplayed>', r'</recordsDisplayed>'],
        'query': [r'<query>', r'</query>']
    }

    result = find_solo(raw_text, patterns['result'])
    total = int(find_solo(result, patterns['total']))
    start = int(find_solo(result, patterns['start']))
    displayed = int(find_solo(result, patterns['displayed']))
    query = find_solo(raw_text, patterns['query'])

    return total, start, displayed, query


def cut_response(raw_text, write_to_file, folder='articles'):

    '''
    cut a single JATS XML response into individual articles

    output(list of strings): a list of single articles

    inputs:
        raw_text(string): text from the response
        write_to_file(boolean): whether or not the individual articles are written to XML files, named by DOI
        folder(string): name of the folder to save XML files
    '''
    
    articles = []
    patterns = [r'<article\s(dtd\-version="[^>\s]+")?', r'</article>']

    if not os.path.exists(folder):
        os.makedirs(folder)
    
    tags = find_tag(raw_text, patterns)
    for tag in tags:
        articles.append(raw_text[tag[0] : tag[3]])
    
    if write_to_file == True:
        for article in articles:
            meta = find_meta(article)
            with open('{}/{}.xml'.format(folder, meta['doi'].replace('/', '_')), 'w', encoding='utf-8') as f:
                f.write(article)
    
    return articles


def split(article, patterns):

    '''
    remove/delete (multiple) contents between a tag pair from the article and store them cut_responsely
    sub-function

    outputs:
        article(string): article without the target contents
        content(list): list of strings of the contents
    
    inputs:
        article(string): full article text
        patterns(list): two regex patterns that mark the tag pair of the information
    '''
    
    content = []
    locations = find_tag(article, patterns)

    for loc in locations:
        content.append(article[loc[0] : loc[3]])

    cut = 0
    for loc in locations:
        article = article[ : loc[0]-cut] + article[loc[3]-cut : ]
        cut += loc[3] - loc[0]

    return article, content


def split_inline(article, patterns):
    '''
    similar to split, but equations and lists need special handling, since they are part of a sentence(periods and colons)
    sub-function

    outputs:
        article(string): article without the equations and lists
        temp(list): a list of equations or lists
    
    inputs:
        article(string): full article text
        patterns(list): two regex patterns that mark the tag pair of equations or lists
    '''

    temp = []

    locations = find_tag(article, patterns)

    for loc in locations:
        temp.append(article[loc[0] : loc[3]])

    # if preceded by a colon(:), replace the colon with a period(. )
    # if preceded by a period(. ), do nothing
    # else, add a period(. )
    cut = 0
    for loc in locations:
        if article[loc[0]-cut-1] == ':':
            article = article[ : loc[0]-cut-1] + '. ' + article[loc[3]-cut : ]
            cut += loc[3] - loc[0] - 1
        elif article[loc[0]-cut-2 : loc[0]-cut] == '. ':
            article = article[ : loc[0]-cut] + article[loc[3]-cut : ]
            cut += loc[3] - loc[0]
        else:
            article = article[ : loc[0]-cut] + '. ' + article[loc[3]-cut : ]
            cut += loc[3] - loc[0] - 2

    return article, temp


def find_tag(text, patterns):

    '''
    find the locations/indices of a tag pair (no nested identical tags)
    sub-function

    output(list): a list of all matches, [start of first tag, end of first tag, start of last tag, end of last tag]

    inputs:
        text(string): the source text
        patterns(list): two regex patterns that mark the tag pair of the information
    '''

    result = []
    matches_s = re.finditer(patterns[0], text)

    if matches_s:
        for match in matches_s:
            match_e = re.search(patterns[1], text[match.end(0) : ])
            if match_e:
                temp = [match.start(0), match.end(0), match.end(0) + match_e.start(0), match.end(0) + match_e.end(0)]
                result.append(temp)
            else:
                # print('No match!!!', patterns[1], '\n')
                return []
    else:
        # print('No match!!!', patterns[0], '\n')
        return []

    return result


def find_solo(text, patterns):

    '''
    slice out information that only appears once in the text (or the first one if multiple matches)
    sub-function

    output(string): the target information

    inputs:
        text(string): the source text
        patterns(list): two regex patterns that mark the tag pair of the information
    '''
    
    match_start = re.search(patterns[0], text)
    if match_start:
        start = match_start.end(0)
    else:
        # print('No match!!!', patterns[0], '\n')
        return ''

    match_end = re.search(patterns[1], text[start : ])
    if match_end:
        end = match_end.start(0)
    else:
        # print('No match!!!', patterns[1], '\n')
        return ''

    result = text[start : end + start]

    return result


def find_multi(text, patterns):

    '''
    slice out information that appear many times in the text
    sub-function

    output(list of strings): the target information

    inputs:
        text(string): the source text
        patterns(list): two regex patterns that mark the tag pair of the information
    '''

    result = []

    tags = find_tag(text, patterns)
    for tag in tags:
        result.append(text[tag[1] : tag[2]])

    return result


def find_meta(article):
    
    '''
    find the metadata of an article

    output(dict): metadata of an article with keys

    inputs:
        article(string): the article text
    '''

    patterns = {
        'front': [r'<front>', r'</front>'],
        'journal-title': [r'<journal\-title>', r'</journal\-title>'], 
        'publisher': [r'<publisher\-name>', r'</publisher\-name>'],
        'doi': [r'<article\-id\spub\-id\-type="doi">', r'</article\-id>'],
        'title': [r'<article\-title[^<]*>', r'</article\-title>'],
        'volume': [r'<volume>', r'</volume>'],
        'page': [r'<elocation\-id>', r'</elocation\-id>'],
        'date': [r'<pub\-date\sdate\-type="pub"\spublication\-format="electronic">', r'</pub\-date>'],
        'day': [r'<day>', r'</day>'],
        'month': [r'<month>', r'</month>'],
        'year': [r'<year>', r'</year>'],
        'issue': [r'<issue[^<]*>', r'</issue>'],
        'contributor': [r'<contrib\-group>', r'</contrib\-group>'],
        'name': [r'<name>', r'</name>'],
        'surname': [r'<surname>', r'</surname>'],
        'given_name': [r'<given\-names>', r'</given\-names>'],
        'access': [r'<license license\-type=', r' xlink']  # oddy
    }

    meta = {
        'doi': None,
        'journal': None,
        'publisher': None,
        'title': None,
        'authors': [], # [[surname1, given_name1], [surname2, given_name2]]
        'volume': None,
        'issue': None,
        'page': None,
        'date': [None, None, None] # [day, month, year]
    }

    article = find_solo(article, patterns['front'])
    meta['doi'] = find_solo(article, patterns['doi'])
    meta['journal'] = find_solo(article, patterns['journal-title'])
    meta['publisher'] = find_solo(article, patterns['publisher'])
    meta['title'] = clean(find_solo(article, patterns['title']))
    meta['volume'] = find_solo(article, patterns['volume'])
    meta['issue'] = find_solo(article, patterns['issue'])
    meta['page'] = find_solo(article, patterns['page'])

    # oddy
    meta['access'] = find_solo(article, patterns['access'])
    # print(meta['access'])

    date = find_solo(article, patterns['date'])
    meta['date'][0] = find_solo(date, patterns['day'])
    meta['date'][1] = find_solo(date, patterns['month'])
    meta['date'][2] = find_solo(date, patterns['year'])

    contributors = find_solo(article, patterns['contributor'])
    names = find_multi(contributors, patterns['name'])
    for name in names:
        author = [find_solo(name, patterns['surname']), find_solo(name, patterns['given_name'])]
        meta['authors'].append(author)

    # [print(key, ':', value) for key, value in meta.items()]
    # print('\n')

    return meta


def clean(text):

    '''
    scrub text from XML tags, references, and non-standard characters. MAY CAUSE PROBLEMS, DO NOT USE UNTIL THE END

    output(string): clean text

    inputs:
        text(string): messy text
    '''

    tags = [
        r'\s?\[?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>[,\–]\s?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>\]?',
        r'\s?\[?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>\]?',
        r'<[^<]+>' # comment out if want to keep tags
    ]

    cleans = [
        ['−', '-'], # en-dash != minus
        [u'\xa0', u' '],
        [u'\u2009', u' '],
        [r'\s{2,100}', ' ',], 
        [r'∼', r'~'],
        ['◦C', '°C'],
        [r'&lt;', r'<'],
        [r'&gt;', r'>'],
        [r'&le;', r'<='],
        [r'&ge;', r'>='],
        [r'(\d+)<sup>(\-?\d+)</sup>', r'\1^\2'] # scientific notation correction
    ]
    
    for clean in cleans:
        text = re.sub(clean[0], clean[1], text)

    for tag in tags:
        text = re.sub(tag, '', text)
    
    return text


def find_abstract(article):

    '''
    find the abstract of an article

    output(list): a list of the paragraphs of the abstract

    inputs:
        article(string): the article text
    '''

    patterns = {
        'abstract': [r'<abstract(\sid="[^>\s]+")?(\sxml:lang="[^>\s]+")?>', r'</abstract>'],
        'par': [r'<p(\sid="[^>\s]+")?>', r'</p>']
    }

    abstract = []
    temp = find_multi(article, patterns['abstract']) # some articles have two abstracts
    for i in temp:
        par = find_multi(i, patterns['par'])
        for j in par:
            abstract.append(clean(j))

    # print(abstract, '\n')

    return abstract


def cut_article(article):
    '''
    divide the article into contents, tables, and figures; remove section titles and labels

    outputs:
        article(string): text contents
        figures(list): list of figure strings
        tables(list): list of table strings
        equations(list): list of equation strings
        lists(list): list of list strings

    inputs:
        article(string): the article text
    '''
    
    patterns = {
        'body': [r'<body>', r'</body>'],
        'tex': [r'<tex\-math(\sid="[^>\s]+")?>', r'</tex\-math>'], # in-line equations
        'fig': [r'<fig(\sid="[^>\s]+")?>', r'</fig>'],
        'table': [r'<table\-wrap(\sid="[^>\s]+")?>', r'</table\-wrap>'],
        'title': [r'<title>', r'</title>'],
        'label': [r'<label>', r'</label>'],
        'equation': [r'<disp\-formula(\sid="[^>\s]+")?>', r'</disp\-formula>'],
        'list': [r'<list(\slist\-type="[^>\s]+")?>', r'</list>']
    }
    
    article = find_solo(article, patterns['body'])
    if article == None:
        return '', [], [], [], []
    else:
        article, figures = split(article, patterns['fig'])
        article, tables = split(article, patterns['table'])
        article, _ = split(article, patterns['title'])
        article, _ = split(article, patterns['label'])
        article, equations = split_inline(article, patterns['equation'])
        article, lists = split_inline(article, patterns['list'])
        article, _ = split(article, patterns['tex'])

    return article, figures, tables, equations, lists


def find_paragraph(content):
    '''
    cut text contents into paragraphs. RUN cut_article FIRST, OR THERE WILL BE NESTED TAGS

    output(list): a list of all paragraphs

    inputs:
        content(string): text content
    '''

    patterns = {
        'body': [r'<body>', r'</body>'],
        'par': [r'<p(\sid="[^>\s]+")?>', r'</p>']
    }

    paragraphs = []
    temp = find_multi(content, patterns['par'])
    for i in temp:
        paragraphs.append(clean(i))

    return paragraphs


def find_caption(figures):
    '''
    d
    '''

    patterns = {
        'caption': [r'<caption(\sxml:lang="\w+")?>', r'</caption>'],
        'p': [r'<p>', r'</p>'],
        'tex': [r'<tex\-math(\sid="[^>\s]+")?>', r'</tex\-math>']
    }

    captions = []
    for figure in figures:
        caption = find_solo(figure, patterns['caption'])
        p = find_multi(caption, patterns['p'])
        for i in p:
            text, tex = split(i, patterns['tex'])
            if text[-1] != '.':
                text += '.'
            captions.append(clean(text))

    return captions


def scrap(s, p, empty, write_to_file, dump_temp, folder='articles'):
    '''
    main function, perform a search and process JATS
    RESULTS ARE DEPENDENT ON ARGUMENT p!!! DONT CHANGE IT

    output(list): a list of articles in dictionaries

    inputs:
        s(int): returned articles start from this number
        p(int): the number of articles in a single query (maximum = 100)
        empty(string): "contain" constraints for the search
        write_to_file(boolean): whether or not the individual articles are written to XML files, named by DOI
        dump_temp(boolean): whether or not to save the raw response to xml files
        folder(string): name of the folder to save XML files
    '''

    raw_text = search_tdmapi(s, p, empty, dump_temp)
    
    articles = cut_response(raw_text, write_to_file, folder)

    total = []
    for article in articles:

        # print(article)
        # print('-'*15)

        meta = find_meta(article)
        abstract = find_abstract(article)
        content, figures, tables, equations, lists = cut_article(article)
        paragraphs = find_paragraph(content)
        captions = find_caption(figures)

        meta['abstract'] = abstract
        meta['paragraphs'] = paragraphs
        meta['captions'] = captions
        meta['tables'] = tables

        total.append(meta)

    return total


def table_processor(total):
    '''
    convert table texts into table objects. If fails, keep table text
    NOT STABLE, USE IT AT YOUR OWN RISK

    output(list): a list of articles in dictionaries, with table_objects & bad_tables instead of tables

    inputs:
        total(list): a list of articles in dictionaries
    '''

    patterns = [r'<tex\-math(\sid="[^>\s]+")?>', r'</tex\-math>'] # tex in tables
    refs = [
        r'\s?\[?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>[,\–]\s?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>\]?',
        r'\s?\[?<xref(\sref\-type="[^>\s]+")?(\srid="\w+")?>\d{1,3}</xref>\]?',
    ]

    for i, article in enumerate(total):
        table_objects = []
        bad_tables = []
        for table in article['tables']:
            table, _ = split(table, patterns)
            for ref in refs:
                table = re.sub(ref, '', table)
            with open('table_temp.html', 'w', encoding='utf-8') as f:
                f.write(table)
            try:
                table_object = Table('table_temp.html')
                table_objects.append(table_object)
            except:
                table_object = str(table)
                # print('bad table:', article['doi'])
                bad_tables.append(str(table))
            
        total[i]['table_objects'] = table_objects
        total[i]['bad_tables'] = bad_tables
        total[i].pop('tables', None)

    if os.path.isfile('table_temp.html'):
        os.remove('table_temp.html')

    return total

from pathlib import Path

if __name__ == "__main__":

    # arguments
    tdm_api_key = '6e29934df62bcf19c148382261f6b5ea'
    meta_api_key = 'bb4db27f82f6cec7f086b45164d173c4'
    s = 1  # let this be
    dump_temp = False
    write_to_file = False

    dois = []  # without any formatting
    access_type = {}

    for year in range(2021, 2023):
        p = 50  # reset every new year or else we get the truncated one from last year
        print(year)
        folder = '2thermoelectric_' + str(year)
        empty = '%22thermoelectric%22%20AND%20year:{}'.format(year)

        # oddy. exploratory run to find total articles per year
        base_url = 'https://articles-api.springer.com/xmldata/jats'
        spr_url = '{}?q={}&excludeElements=Bibliography&api_key={}&s={}&p={}'.format(base_url, empty, tdm_api_key, s, p)
        sav_name = '{}_s={}_p={}.xml'.format(empty, s, p).replace(':', "=").replace('%22', "").replace('%20', "_")
        response = requests.get(spr_url)
        if response:
            total_articles, start, displayed, query = get_total(response.text)
            # print(total_articles)

        # go over rounds (p articles every round)
        for round in range(total_articles // p + 1):
            start = round * p
            end = (round + 1) * p
            p = p if end < total_articles else p - end + total_articles  # for last step to not exceed articles total
            print(f"{str(start)} - {str(start + p)} / {str(total_articles)}")

            # search
            total = scrap(start, p, empty, write_to_file, dump_temp, folder)
            total = table_processor(total)
            fpath = os.path.join('/Users/ody/Desktop/BERT/2SPR', folder)

            for article in total:
                original_doi = article['doi']
                dois.append(original_doi)
                access = 'yes' if (article['access'] == '"open-access"') else 'no'
                access_type[original_doi] = access
                # print(original_doi, 'open: ', access)


            if True:
                if not os.path.isdir(fpath):
                    os.mkdir(fpath)

                # write text and save pickle
                for i, article in enumerate(total):
                    doi = article['doi'].replace('/', '-')
                    fname = os.path.join(fpath, 'article-' + doi + '.txt')
                    # print(start + i + 1, doi, len(article['paragraphs']))

                    # try:
                    #     print(article["title"])
                    # except Exception:
                    #     print("Couldn't get title")

                    with open(fname.replace("txt", 'pickle'), 'wb') as pk:
                        pickle.dump(article, pk)

                    with open(fname, 'w', encoding='utf-8') as f:
                        f.write(article['title'] + '\n\n')
                        f.write(article['journal'] + '\n')
                        f.write(r"/".join(article['date']) + '\n')
                        f.write(", ".join(" ".join(x) for x in article['authors']) + "\n\n")

                        f.write('Abstract:\n')
                        for abstract in article['abstract']:
                            f.write(abstract + '\n')
                        f.write("\n\n")

                        for paragraph in article['paragraphs']:
                            f.write(paragraph + '\n\n')

        print('-' * 22 + '\n')

print(len(dois))
with open('/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/springer_dois.pkl','wb') as pk:
    pickle.dump(dois, pk)

with open('/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/springer_access_types_by_doi.pkl','wb') as pk:
    pickle.dump(access_type, pk)

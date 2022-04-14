from pprint import pprint
from chemdataextractor import Document
import pandas as pd

from chemdataextractor.model.units.thermoelectric_models import ThermCond
from chemdataextractor.split_and_stitch.new_parsing import te_parse

#new change:
from chemdataextractor.parse.expressions_for_models import processing_expression, direction_expression, contextual_label_expression, editing_expression

filename = "article-10.1016-j.jssc.2014.12.010.xml"
doc_path = "test_articles/" + filename

d = Document.from_file(doc_path)
d.models = [ThermCond]

rec = d.records.serialize()
pprint(rec)


df1 = pd.DataFrame()
records_holder = []
print("te parsing:")
df1, records_holder = te_parse(d, df1, records_holder, filename, 'title', given_model=ThermCond)

df1.to_csv("example_database.csv")
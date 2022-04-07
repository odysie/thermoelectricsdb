from chemdataextractor import Document
from pprint import pprint

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

from chemdataextractor.model.units.thermoelectric_models import ThermCond

#new change:
from chemdataextractor.parse.expressions_for_models import processing_expression, direction_expression, contextual_label_expression, editing_expression

doc_path = "/Users/ody/Desktop/SC/THESIS/py_tests/downloaded_articles/ALL_RSC/article-10.1039-c6ra24053d.html"

d = Document.from_file(doc_path)
d.models = [ThermCond]

rec = d.records.serialize()
pprint(rec)

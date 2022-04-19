#Oddy: create a new boiling point parsing logic
#according to cde docs example in page 19 (23/236)

from chemdataextractor.parse import R, I, W, Optional, merge
from chemdataextractor.parse.base import BaseParser
from chemdataextractor.utils import first

#parsing rules:

prefix = (R(u'^b\.?p\.?', re.I) | I(u'boiling') + I(u'point')).hide()
units = (W(u'°') + Optional(R(u'^[CFK]\.?$)))(u'raw_units).add_action(merge)
value = R(u'^\d+(\.\d+)?$')(u'raw_value')
bp = (prefix + value + units)(u'bp')

"""
explanation:
prefix matches b with optional full stop, and p with optional full stop, i.e. bp or b.p. and is case insensitive or boiling point altogether, and hides in the relationship tree.
units match C or F or K with an optional full stop at the end, and are tagged with raw units. 
value matches any number of digits followed optionally by a full stop which is further followed by other digits, representing decimals.
values is tagged with raw_value
bp is then prefix, value, and units together. tagged with bp
"""


#logic for parsing the structure, which must include:
root variable: the phrase that forms the head of the tree
interpret function: defines the parsing logic

class BpParser(BaseSentenceParser):
    root = bp

    def interpret(self, result, start, end):
	try:
	    raw_value = first(result.xpath('./value/text()')
	    raw_units = first(result.xpath('./units/text()')
	    boiling_point = self.model(raw_value=raw_value,
			raw_units=raw_units,
			value=self.extract_value(raw_value)
			error=self.extract_error(raw_value)
			units=self.extract_units(raw_units,strict=True))
	    yield boiling_point
	expect TypeError as e:
	    log.debug(e)


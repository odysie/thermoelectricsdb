"""
Parses articles into a raw database, as done during the thermoelectric materials project.

"""

import os
from chemdataextractor import Document
import pandas as pd

from chemdataextractor.model.units.thermoelectric_models import ThermCond
from chemdataextractor.split_and_stitch.new_parsing import te_parse

folder = os.path.join(os.path.dirname(__file__), "test_articles")
chosen_model = ThermCond

df1 = pd.DataFrame()
records_holder = []

for article in [f for f in os.listdir(folder) if f.startswith("article")]:
    article_path = os.path.join(folder, article)

    d = Document.from_file(article_path)
    d.models = chosen_model

    print("Processing", article, ". . .")

    try:
        title = d.titles[0].text
        print('Title: ' + title + ':\n')
    except (IndexError, UnicodeError):
        title = "title_fail"
        print("Couldn't get title.")  # the titles will fail for text files from Springer. Added post-extraction.

    df1, records_holder = te_parse(d, df1, records_holder, filename=article, title=title,
                                   given_model=chosen_model)

    print()

df1.to_csv("example_database.csv")
print("Done. The resulting 'example_database.csv' holds", len(df1), "records.")
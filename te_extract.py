from chemdataextractor_thermoelectrics.chemdataextractor.model.units.thermoelectric_models import PF

from chemdataextractor import Document
import pandas as pd

from parsing_architecture import v_parse

pf_test_paths = ['/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/CENTRALISE_RECALL/Centralised_Articles/article-10.1016-j.jmat.2017.06.002.xml',
                 '/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/CENTRALISE_RECALL/Centralised_Articles/article-10.1016-j.matdes.2019.108263.xml',
                 '/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/CENTRALISE_RECALL/Centralised_Articles/article-10.1016-j.rinp.2018.06.053.xml',
                 '/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/CENTRALISE_RECALL/Centralised_Articles/article-10.1039-c7sc05190e.html']


for model in [PF]:
    chosen_model = model

    for pf_path in pf_test_paths:
        print(f"*MODEL name: {chosen_model.__name__}*\n")

        # d1 = Document(Paragraph(p), models=[chosen_model])
        # d2 = Document(Paragraph(p), models=[chosen_model]) # do we need two documents to parse normally as well?

        #test_file_path = "/Users/ody/Desktop/SC/THESIS/DATA/good/V_STUFF/Springer_Recall_new/Springer_recall_text_files/10.1007-s10973-012-2192-y.txt"
        with open(pf_path, 'rb') as f:
            d1 = Document.from_file(f)

        df1 = pd.DataFrame()
        records_holder = []
        # print(f"Sentence:\n{p}\n")

        print("V parsing:")
        df1 = v_parse(d1, df1, records_holder, 'doi', 'title', given_model=chosen_model, printing=True)  #enable printing for local tests, but do not do it on Cooley
        print()

        # print('NORMAL parsing:')
        # pprint(d2.records.serialize())
        # print()

        # print("tagged tokens:")
        # for el in d1.elements:
        #     print(el.tagged_tokens)
        # print("Cems:", d1.cems)
        # print(f"\n*MODEL name: {chosen_model.__name__}*\n")
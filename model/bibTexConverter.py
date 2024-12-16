import os
import re
import uuid

from citeproc import CitationStylesStyle, CitationStylesBibliography, formatter, CitationItem, Citation
from citeproc.source.bibtex import BibTeX
import warnings

from model.utils import remove_consecutive_spaces

warnings.filterwarnings('ignore')


def warn(citation_item):
    print("WARNING: Reference with key '{}' not found in the bibliography."
          .format(citation_item.key))


class BibTexConverter:
    def __init__(self):
        project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.bib_style = CitationStylesStyle(f'{project_dir}/data/styles/gb7714-1987.csl',
                                             validate=False)

    def convert_text(self, text: str):
        text = text.replace(r'$\{', '').replace(r'\}$', '').replace('$', '')
        mts = re.findall(r'(\{\\"(.*?)})', text)
        for mt in mts:
            text = text.replace(mt[0], mt[1])
        filename = f'{uuid.uuid4().hex}.bib'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        try:
            result = self.convert(filename)
        finally:
            os.remove(filename)
        return result

    def convert(self, filename: str):
        bib_source = BibTeX(filename)
        key = list(bib_source.keys())[0]
        citation = Citation([CitationItem(key)])

        bibliography = CitationStylesBibliography(self.bib_style, bib_source,
                                                  formatter.plain)
        bibliography.register(citation)
        bibliography.cite(citation, warn)
        for item in bibliography.bibliography():
            cite = str(item).replace('–', '-').replace('等', 'et al').replace('\n', '')
            return remove_consecutive_spaces(cite)


if __name__ == '__main__':
    converter = BibTexConverter()
    print(converter.convert('../result/1.bib'))

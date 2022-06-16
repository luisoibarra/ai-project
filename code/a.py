from typing import Dict, Tuple
from corpus_parser.test.bret_test import test_parse as bret_test
from corpus_parser.test.conll_test import test_parse as conll_test, test_from_dataframe

from corpus_parser.bret_parser import BretParser
from corpus_parser.conll_parser import ConllParser
from pathlib import Path

# bret_test()

# conll_test()

# test_from_dataframe()

# pa = ConllParser(".en", ".de", ".zh", ".es")
pa = BretParser()

r = pa.parse_dir(Path(".") / "corpus" / "testing")

d = pa.from_dataframes(r)

def export_corpus(dest_address: Path, files: Dict[str,Tuple[str,str]]):
    if not dest_address.is_dir():
        dest_address.mkdir()
        
    for filedir, (annotated_text, raw_text) in files.items():
        name = Path(filedir).name
        dest = dest_address / name
        dest.write_text(annotated_text)
        dest = dest_address / (name + ".txt")
        dest.write_text(raw_text)

export_corpus(Path(".")/"parsed_corpus"/"testing", d)